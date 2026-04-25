import 'dart:io';
import 'dart:developer' as developer;
import 'package:firebase_storage/firebase_storage.dart';
import '../../domain/repository/storage_repository.dart';

class StorageRepositoryImpl implements StorageRepository {
  final FirebaseStorage _firebaseStorage;

  StorageRepositoryImpl(this._firebaseStorage);

  @override
  Future<String> uploadImage(File image, String userId) async {
    try {
      // Basic validation
      if (!await image.exists()) {
        throw Exception("El archivo seleccionado no existe en el sistema.");
      }
      
      final fileSize = await image.length();
      developer.log('Iniciando subida. Tamaño: ${fileSize / 1024} KB. Usuario: $userId', name: 'SymmetryStorage');

      final extension = image.path.split('.').last.toLowerCase();
      final mimeType = extension == 'webp' ? 'image/webp' : (extension == 'png' ? 'image/png' : 'image/jpeg');
      
      final fileName = "art_${DateTime.now().millisecondsSinceEpoch}.$extension";
      final path = 'users/$userId/articles/$fileName';
      final ref = _firebaseStorage.ref().child(path);
      
      developer.log('Destino en Storage: $path (Mime: $mimeType)', name: 'SymmetryStorage');
      
      // Start upload task
      final uploadTask = ref.putFile(
        image,
        SettableMetadata(contentType: mimeType),
      );
      
      // Wait for completion with more robustness
      final snapshot = await uploadTask.whenComplete(() => null);
      
      if (snapshot.state == TaskState.success) {
        final downloadUrl = await snapshot.ref.getDownloadURL();
        developer.log('Subida completada con éxito. URL: $downloadUrl', name: 'SymmetryStorage');
        return downloadUrl;
      } else {
        throw Exception("La subida no se completó correctamente. Estado: ${snapshot.state}");
      }

    } catch (e) {
      developer.log('ERROR CRÍTICO STORAGE: $e', name: 'SymmetryStorage', error: e);
      
      if (e is FirebaseException) {
        developer.log('Código Firebase: ${e.code}', name: 'SymmetryStorage');
        developer.log('Mensaje Firebase: ${e.message}', name: 'SymmetryStorage');
        
        if (e.code == 'unauthorized') {
          throw Exception("Error de permisos: Revisa las reglas de seguridad de Firebase Storage.");
        } else if (e.code == 'canceled') {
          throw Exception("La subida fue cancelada.");
        }
      }
      
      throw Exception("Error al subir la imagen: ${e.toString()}");
    }
  }
}

