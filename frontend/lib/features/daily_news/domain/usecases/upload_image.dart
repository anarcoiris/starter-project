import 'dart:io';
import '../repository/storage_repository.dart';

class UploadImageUseCase {
  final StorageRepository _storageRepository;

  UploadImageUseCase(this._storageRepository);

  Future<String?> call({required File image, required String userId}) {
    return _storageRepository.uploadImage(image, userId);
  }
}
