import rsa
import zlib
import base64

def encrypt_blob(blob, public_partner):
    # In determining the chunk size, determine the private key length used in bytes
    # and subtract 42 bytes (when using PKCS1_OAEP). The data will be in encrypted
    # in chunks
    chunk_size = 86
    offset = 0
    end_loop = False
    encrypted = b""

    while not end_loop:
        # The chunk
        chunk = blob[offset:offset + chunk_size]

        # If the data chunk is less then the chunk size, then we need to add
        # padding with " ". This indicates the we reached the end of the file
        # so we end loop here
        if len(chunk) % chunk_size != 0:
            end_loop = True
            chunk += " " * (chunk_size - len(chunk))

        # Append the encrypted chunk to the overall encrypted file
        encrypted += rsa.encrypt(chunk.encode(), public_partner)

        # Increase the offset by chunk size
        offset += chunk_size

    # Base 64 encode the encrypted file
    return base64.b64encode(encrypted)


def decrypt_blob(encrypted_blob, private_key):

    # Base 64 decode the data
    encrypted_blob = base64.b64decode(encrypted_blob)

    # In determining the chunk size, determine the private key length used in bytes.
    # The data will be in decrypted in chunks
    chunk_size = 128
    offset = 0
    decrypted = ""

    # keep loop going as long as we have chunks to decrypt
    while offset < len(encrypted_blob):
        # The chunk
        chunk = encrypted_blob[offset: offset + chunk_size]

        # Append the decrypted chunk to the overall decrypted file
        decrypted += rsa.decrypt(chunk, private_key).decode()

        # Increase the offset by chunk size
        offset += chunk_size

    return decrypted


public,private = rsa.newkeys(1024)

message = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam in metus non mauris fermentum lobortis et sed eros. Vestibulum ut velit lorem. Pellentesque varius urna quis tortor placerat, quis finibus nunc condimentum. Nulla vehicula pellentesque dui vitae convallis. Fusce sit amet libero turpis. Maecenas eleifend ultricies aliquet. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Ut sagittis urna orci, eu pulvinar risus vehicula non. Donec sollicitudin condimentum odio, dictum hendrerit felis imperdiet vel. Vivamus pretium, ligula a egestas varius, leo nunc laoreet ex, et vehicula mauris quam id mauris. Suspendisse blandit purus et eros tincidunt dignissim. Morbi fermentum ornare commodo. Sed sed orci vel velit consectetur varius. Donec quis justo libero.

Donec sed sollicitudin dui. Fusce efficitur aliquam justo eu sollicitudin. Maecenas eu auctor sem. Quisque ut ultrices urna, sed sodales risus. Ut pellentesque ante eu posuere condimentum. Sed a magna eu ipsum facilisis dignissim vel sed velit. In ante velit, fringilla non vulputate vitae, sodales vitae mauris. In varius elit ut suscipit iaculis. Proin ipsum nisl, dictum id metus et, egestas tristique massa. Quisque tempor, est et sodales egestas, quam diam consectetur elit, eget tempor enim diam non quam. Morbi scelerisque dignissim sem a auctor. Fusce congue massa odio, rhoncus ultricies libero consequat eu. Praesent non nunc vehicula lorem sagittis congue.

Pellentesque turpis risus, faucibus ut scelerisque sed, scelerisque in nulla. Sed mollis nulla vitae nibh vulputate suscipit. Nam a nunc at quam semper auctor. Curabitur tincidunt est vitae sem tristique, id luctus arcu scelerisque. Sed justo lorem, sollicitudin ut odio eu, lacinia rutrum lectus. Proin vitae tellus sed enim fringilla laoreet. Vivamus eget imperdiet sapien. Nulla suscipit, mi eu ultrices imperdiet, justo felis fermentum orci, sit amet ornare nulla odio et metus. Vivamus volutpat mauris nec volutpat luctus. Integer aliquam, turpis vel consectetur interdum, odio sem tempor nisl, fermentum gravida arcu felis non leo. Maecenas faucibus leo lobortis urna iaculis commodo.

In et nisl interdum orci pellentesque pulvinar eu non felis. Vestibulum sed ex aliquet purus dapibus cursus. Nullam metus mi, mattis in imperdiet ac, accumsan et lacus. Aenean ornare ex maximus, cursus risus eget, auctor justo. Nunc eget ligula id augue volutpat lobortis eget id ligula. Duis non rutrum risus. Mauris mollis risus arcu, placerat commodo ipsum rhoncus non. Quisque ut nunc eget velit mollis consequat. Aenean aliquam, leo eget vehicula dignissim, nisi purus ultricies nunc, id dictum erat leo sit amet magna. Donec lacinia ultricies nisi sit amet rhoncus. Fusce et sapien tortor. Nullam pulvinar vitae mauris vel bibendum. Nunc a ultrices orci, in maximus arcu. Aliquam non orci a ante malesuada rutrum. Aenean viverra nec velit vitae scelerisque. Mauris in erat malesuada, porttitor ante a, euismod velit.

Aliquam vitae tellus tellus. Mauris condimentum, felis in tincidunt varius, odio eros imperdiet nisi, ac finibus nisl quam vitae magna. Interdum et malesuada fames ac ante ipsum primis in faucibus. Vivamus pellentesque, ligula in fermentum dapibus, mi lectus ullamcorper nisl, rhoncus pharetra mi purus sit amet nibh. Integer vel mauris finibus, suscipit est vel, laoreet enim. Sed consequat ultricies ex eu elementum. Cras ac odio dui. Sed tempus rhoncus enim, mollis laoreet leo faucibus a. Nullam mattis odio non ex pellentesque aliquam. Maecenas venenatis sollicitudin hendrerit.'''
# message = message.encode()

encrypted = encrypt_blob(message,public)
print(encrypted)
print()
decrypted = decrypt_blob(encrypted,private)
print(decrypted)