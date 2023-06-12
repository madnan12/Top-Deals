import re
import boto3
import random
import string
import subprocess
from PIL import Image, ImageOps
from django.conf import settings

def password_validator(password):
    return True if re.search(re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!¬#%*?&_()-^=+£/,.])[A-Za-z\d@$!¬#%*?&_()-^=+£/,.]{8,100}$"), password) else False


def email_validator(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    email_validation = re.search(regex, email)
    return email_validation

def compress_saved_image(input_image):
    # Get the image name

    image_name = str(input_image)
    extension = image_name.split(".")[-1]
    image_name = image_name.split(".")[0]
    # Open Image through Pillow and Compress it
    input_image = Image.open(input_image)
    input_image = ImageOps.exif_transpose(input_image)
    input_image = input_image.convert('RGB')
    img_width = input_image.size[0]
    img_height = input_image.size[1]
    x = img_width / 800
    y = int(img_height // x)
    input_image = input_image.resize((800, y))
    random_digits_for_image = ''.join(
        random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(10))
    input_image.save(f"{image_name}_{random_digits_for_image}.jpeg", format='JPEG', quality=80)
    new_image = f"{image_name}_{random_digits_for_image}.jpeg"
    subprocess.call("rm " + image_name + "." + extension, shell=True)
    return new_image


def upload_to_bucket(input_file, output_file):
    session = boto3.Session(
        aws_access_key_id= settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY,
    )
    s3 = session.resource('s3')
    filename = input_file
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    key = output_file
    s3.meta.client.upload_file(Filename=filename, Bucket=bucket, Key=key)


def create_slug(name=None, title=None, slugs=[]):
    non_url_safe = ['"', '#', '$', '%', '&', '+', '*',
                    ',', '/', ':', ';', '=', '?',
                    '@', '[', '\\', ']', '^', '`',
                    '{', '|', '}', '~', "'", '.']
    if name:
        name = name.lower()
        for i in non_url_safe:
            if i in name:
                name = name.replace(i, ' ')
        slug = name.replace(' ', '-')
        slug = slug.replace('--', '-')
        if slug in slugs:
            random_digits_for_slug = ''.join(
                random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(4))
            slug = f"{slug}-{random_digits_for_slug}"
        return slug
    elif title:
        title = title.lower()
        for i in non_url_safe:
            if i in title:
                title = title.replace(i, ' ')
        slug = title.replace(' ', '-')
        slug = slug.replace('--', '-')
        if slug in slugs:
            random_digits_for_slug = ''.join(
                random.SystemRandom().choice(string.hexdigits + string.hexdigits) for _ in range(4))
            slug = f"{slug}-{random_digits_for_slug}"
        return slug


def unique_item_name():
    pass