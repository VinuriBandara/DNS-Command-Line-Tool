from google.cloud import storage
import os
import io
from concurrent.futures import ProcessPoolExecutor

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_app_cred.json"


def scanComplete():
    # check if the scan is complete 
    return True


# get the blob size
def blob_size(bucket_name, source_blob_name):

    storage_client = storage.Client()
 
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(source_blob_name)
    blobSize = blob.size
    return blobSize

#download blob as whole
# def download_blob(bucket_name, source_blob_name, destination_file_name):
 
#     storage_client = storage.Client()
 
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(source_blob_name)
#     blob.download_to_filename(destination_file_name)
 
#     print(
#         "Blob {} downloaded to file path {}. successfully ".format(
#             source_blob_name, destination_file_name
#         )
#     )



# split the blob into chunks
def split_byte_size(size: int, bucket: str, key: str) -> list:
    print(size)
    byte_list = []
    split = int(size/5)
    byte_list.append({"start": 0, "end": split, "bucket": bucket, "key": key})
    byte_list.append({"start": split+1, "end": (split+1)+split, "bucket": bucket, "key": key})
    byte_list.append({"start": (split+1)*2, "end": ((split+1)*2)+split, "bucket": bucket, "key": key})
    byte_list.append({"start": (split+1)*3, "end": size, "bucket": bucket, "key": key})
    byte_list.append({"start": (split+1)*4, "end": size, "bucket": bucket, "key": key})
    return byte_list

# download the blob 
def downloader(input: dict) -> object:
    storage_client = storage.Client()
    bucket_object = storage_client.get_bucket(input["bucket"])
    blob = bucket_object.blob(input["key"])
    in_memory_file = io.BytesIO()
    blob.download_to_file(in_memory_file, start=input["start"], end=input["end"])
    return in_memory_file

if __name__ == '__main__':
    bucket_object = 'dnstest_bucket_1'
    blob = 'blob_dns'
    dest_file = 'results/download_json.json'

    status = scanComplete()

    if status:
        Blob_size = blob_size(bucket_object,blob)
        split_bytes = split_byte_size(Blob_size, bucket_object, blob)
        with ProcessPoolExecutor(5) as ex:
            results = ex.map(downloader, split_bytes)
        in_memory_file = io.BytesIO()
        for result in results:
            print(result)
            result.seek(0)
            in_memory_file.write(result.getbuffer())
        in_memory_file.seek(0)
        with open(dest_file, "wb") as outfile:
        #write the IO file to destination file
            outfile.write(in_memory_file.getbuffer())