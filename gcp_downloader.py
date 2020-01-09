from google.cloud import storage
import sys


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )

if __name__ == "__main__":
    bucket_name = sys.argv[1]
    file_name = sys.argv[2]
    if len(sys.argv) < 4: position = ""
    else: position = sys.argv[3]
    download_blob(bucket_name, position+file_name, '/home/'+file_name)