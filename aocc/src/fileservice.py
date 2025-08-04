from aocc.src.service import Service, Connection, Package
import os
from time import sleep

class FileService(Service):

    def __init__(self, conn_in: Connection, conn_out: Connection):
        super(FileService, self).__init__(name='FileService', conn_in=conn_in, conn_out=conn_out, request_callback=self._request_callback, response_callback=self._response_callback, config_required=False)
        self.start()
        while self.isRunning:
            sleep(0.5)

    def _request_callback(self, package: Package) -> None:
        match package.Subject:
            case 'file_exists':
                if package.Payload != None:
                    
                    try:
                        file: str = package.Payload['file']
                    except:
                        file: None = None

                    if file != None:        
                        result: bool = self._file_exists(file=file)
                        response: Package = Package(
                            sender=self._name,
                            recipent=package.Sender,
                            package_type='response',
                            package_id=package.PackageID,
                            subject=package.Subject,
                            code=200,
                            payload={
                                'file': file,
                                'exists': result
                            }
                        )
                    else:
                        response: Package = self._create_wrong_payload_response(package=package)
                else:
                    response: Package = self._create_no_payload_response(package=package)
                self.send_package(package=response)
            
            case 'get_file_data':
                if package.Payload != None:
                    
                    try:
                        file: str = package.Payload['file']
                    except:
                        file: None = None

                    if file != None:
                        file_data: bytes = self._read_file_bytes(file=file)
                        response: Package = Package(
                            sender=self._name,
                            recipent=package.Sender,
                            package_type='response',
                            package_id=package.PackageID,
                            subject=package.Subject,
                            code=200,
                            payload={
                                'file': file,
                                'exists': True,
                                'length': len(file_data),
                                'data': file_data
                            }
                        )
                    else:
                        response: Package = self._create_wrong_payload_response(package=package)
                else:
                    response: Package = self._create_no_payload_response(package=package)
                self.send_package(package=response)    
            
            case 'put_file_data':
                if package.Payload != None:
                    
                    try:
                        file: str = package.Payload['file']
                        file_data: bytes = package.Payload['data']
                    except:
                        file: None = None
                        file_data: None = None

                    if file != None and file_data != None:
                        result: bool = len(file_data) == self._write_file_bytes(file=file, data=file_data)
                        response: Package = Package(
                            sender=self._name,
                            recipent=package.Sender,
                            package_type='response',
                            package_id=package.PackageID,
                            subject=package.Subject,
                            code=200,
                            payload={
                                'file': file,
                                'exists': True,
                                'written_bytes': len(file_data),
                                'written': result
                            }
                        )
                    else:
                        response: Package = self._create_wrong_payload_response(package=package)
                else:
                    response: Package = self._create_no_payload_response(package=package)
                self.send_package(package=response)

            case _:
                pass

    def _response_callback(self, package: Package) -> None:
        pass

    def _file_exists(self, file: str) -> bool:
        return os.path.exists(file)
    
    def _is_file(self, file: str) -> bool:
        return os.path.isfile(file)
    
    def _read_file_bytes(self, file: str) -> bytes:
        try:
            with open(file=file, mode='rb') as input_file:
                file_data: bytes = input_file.read()
        except:
            file_data: bytes = bytes()
        finally:
            return file_data

    def _write_file_bytes(self, file: str, data: bytes) -> int:
        if not os.path.isdir(file) and self._is_file(file=file):
            try:
                with open(file=file, mode='wb') as output_file:
                    result: int = output_file.write(data) 
            except:
                result: int = int(0)
            finally:
                return result
        return int(0)

    def _create_no_payload_response(self, package: Package) -> Package:
        return Package(
            sender=self._name,
            recipent=package.Sender,
            package_type='response',
            package_id=package.PackageID,
            subject=package.Subject,
            code=501,
            payload={
                'data': 'No Payload was set for Package',
                'package': package
            }
        )
    
    def _create_wrong_payload_response(self, package: Package) -> Package:
        return Package(
            sender=self._name,
            recipent=package.Sender,
            package_type='response',
            package_id=package.PackageID,
            subject=package.Subject,
            code=502,
            payload={
                'data': 'Wrong Payload',
                'package': package
            }
        )