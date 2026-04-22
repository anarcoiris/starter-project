import 'dart:io';
import 'dart:developer' as developer;
import 'package:firebase_storage/firebase_storage.dart';
import '../domain/repository/storage_repository.dart';

class StorageRepositoryImpl implements StorageRepository {
  final FirebaseStorage _firebaseStorage;

  StorageRepositoryImpl(this._firebaseStorage);

  @override
  Future<String> uploadImage(File image, String userId) async {
    try {
      final fileName = "${DateTime.now().millisecondsSinceEpoch}.jpg";
      final path = 'users/$userId/articles/$fileName';
      final ref = _firebaseStorage.ref().child(path);
      
      developer.log('Iniciando subida de imagen: $path', name: 'SymmetryStorage');
      
      final uploadTask = await ref.putFile(
        image,
        SettableMetadata(contentType: 'image/jpeg'),
      );
      
      final downloadUrl = await uploadTask.ref.getDownloadURL();
      developer.log('Imagen subida con éxito: $downloadUrl', name: 'SymmetryStorage');
      return downloadUrl;
    } catch (e) {
      developer.log('Error en Firebase Storage: $e', name: 'SymmetryStorage', error: e);
      throw Exception("Error al subir la imagen a la nube: $e");
    }
  }
}
