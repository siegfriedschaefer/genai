
import time
import urllib

from PIL import Image as PIL_Image
from google import genai
from google.genai import types
from google.cloud import storage

import matplotlib.pyplot as plt
import mediapy as media

import os

PROJECT_ID = "veo3-get-started"  # @param {type: "string", placeholder: "[your-project-id]", isTemplate: true}
if not PROJECT_ID or PROJECT_ID == "[your-project-id]":
    PROJECT_ID = str(os.environ.get("GOOGLE_CLOUD_PROJECT"))

LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")

print(f"PROJECT_ID: {PROJECT_ID}")
print(f"LOCATION: {LOCATION}")

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def show_video(gcs_uri):
    file_name = gcs_uri.split("/")[-1]
    print(f"Downloading {gcs_uri} to {file_name}")
    download_blob(
        bucket_name=gcs_uri.split("/")[2],
        source_blob_name="/".join(gcs_uri.split("/")[3:]),
        destination_file_name=file_name,
    )
#    !gsutil cp {gcs_uri} {file_name}
#    media.show_video(media.read_video(file_name), height=500)


def display_images(image) -> None:
    fig, axis = plt.subplots(1, 1, figsize=(12, 6))
    axis.imshow(image)
    axis.set_title("Starting Image")
    axis.axis("off")
    plt.show()

video_model = "veo-2.0-generate-001"

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print(f"Client created: {client}")

prompt = "A european brown bear walking trough a field of flowers in front of the Rosengarden massiv from the right image border to left"  # @param {type: 'string'}
aspect_ratio = "16:9"  # @param ["16:9", "9:16"]
output_gcs = "gs://video-generation-001/output"  # @param {type: 'string'}

operation = client.models.generate_videos(
    model=video_model,
    prompt=prompt,
    config=types.GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
        output_gcs_uri=output_gcs,
        number_of_videos=1,
        duration_seconds=5,
        person_generation="dont_allow",
        enhance_prompt=True,
    ),
)

while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)
    print(operation)

if operation.response:
    show_video(operation.result.generated_videos[0].video.uri)




