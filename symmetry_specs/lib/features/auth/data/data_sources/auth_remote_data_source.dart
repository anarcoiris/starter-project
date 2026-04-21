import '../models/auth_model.dart';

/// ONLY class allowed to talk to the remote API / Firestore.
abstract class AuthRemoteDataSource {
  Future<List<AuthModel>> getAll();
  Future<AuthModel> getById(String id);
  Future<AuthModel> create(AuthModel model);
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  // TODO: inject HTTP client or Firestore instance

  @override
  Future<List<AuthModel>> getAll() async {
    // TODO: implement
    throw UnimplementedError();
  }

  @override
  Future<AuthModel> getById(String id) async {
    throw UnimplementedError();
  }

  @override
  Future<AuthModel> create(AuthModel model) async {
    throw UnimplementedError();
  }
}
