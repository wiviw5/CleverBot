"""
This file is a part of the module "Files utils"

All Files related to this module:
utils/files_utils.py

This is just for making downloads & telling what type of files are being downloaded. Specialty file manipulation are done in module's specific utils files.
"""
import httpx
import hashlib

from httpx import Response


def getFileExtensionType(fileBytes: Response) -> str:
    content_type = str(fileBytes.headers.get("content-type"))
    match content_type:
        case "text/plain":
            return ".txt"
        case "image/png":
            return ".png"
        case "image/jpeg":
            return ".jpg"
        case "image/gif":
            return ".gif"
        case "image/webp":
            return ".webp"
        case "video/mp4":
            return ".mp4"
        case "video/webm":
            return ".webm"
        case "video/quicktime":
            return ".mov"
        case _:
            unknownType = content_type.split("/")[1]
            return f"_UNKNOWN_{unknownType}.txt"


# Returns true if the size of the file is under discords upload threshold for default servers
# Old max file size limit was 8 MB (8388608 Bytes)
# New max file size as of 4/10/23 for users & is now 25 MB (26214400 Bytes) [Size limit of 8MB was fixed here on 4/13/23: https://github.com/discord/discord-api-docs/issues/6058]
def checkFileSize(Bytes):
    return len(Bytes.content) <= 26214400


def getFileSize(RB):
    ByteValue = len(RB)
    if ByteValue <= 1024:
        return f"{ByteValue} Bytes"
    elif ByteValue <= 1048576:
        return f"{'%.2f' % translateBytesIntoKB(ByteValue)} KB"
    else:
        return f"{'%.2f' % translateBytesIntoMB(ByteValue)} MB"


def translateBytesIntoKB(incomingBytes):
    return incomingBytes / 1024


def translateBytesIntoMB(incomingBytes):
    return incomingBytes / 1048576


def getHashOfBytes(incomingBytes):
    h = hashlib.sha256()
    h.update(incomingBytes)
    return h.hexdigest()


headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.3"}


async def downloadURL(url) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        return r
