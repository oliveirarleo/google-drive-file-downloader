class FileManager:        
    @staticmethod
    def save_response_content(response, destination, file_size):
        CHUNK_SIZE = 32768
        # for downloading large file with progress bar
        if file_size > CHUNK_SIZE:
            with open(destination, "wb") as file:
                with tqdm(total=file_size, unit='bytes', unit_scale=True) as pbar:
                    for chunk in response.iter_content(CHUNK_SIZE):
                        pbar.update(CHUNK_SIZE)
                        if chunk:  # filter out keep-alive new chunks
                            file.write(chunk)
        # for downloading small files in one chunk
        else:
            with open(destination, "wb") as file:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        file.write(chunk)
                        
    @staticmethod
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    @staticmethod
    def download_file_from_google_drive(id, destination):
        if not os.path.isfile(destination):
            dirs = os.path.dirname(destination)
            if not os.path.exists(dirs):
                os.makedirs(dirs)

            URL = "https://drive.google.com/uc?export=download"

            session = requests.Session()
            headers = {'range': 'bytes=0-'}
            response = session.get(URL, params = { 'id' : id }, headers=headers, stream = True)

            token = FileManager.get_confirm_token(response)

            if token:
                params = { 'id' : id, 'confirm' : token }

                response = session.get(URL, params = params, headers=headers, stream = True)

            cr = response.headers.get('content-range')
            total_size = int(cr.rsplit('/', 1)[1])

            FileManager.save_response_content(response, destination, total_size)
        else:
            print('File ' + destination +' already exists.')

    @staticmethod
    def extract_tar(origin, destination):
        if os.path.isfile(origin) and not os.path.exists(destination):
            os.makedirs(destination)
            with tarfile.open(origin) as tf:
                tf.extractall(destination)
        else:
            print('Folder ' + destination + ' already exists.')

    @staticmethod
    def extract_zip(origin, destination):
        if os.path.isfile(origin) and not os.path.exists(destination):
            os.makedirs(destination)
            with zipfile.ZipFile(origin, 'r') as zf:
                zf.extractall(destination)
        else:
            print('Folder ' + destination + ' already exists.')

    @staticmethod
    def rm_folder(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))