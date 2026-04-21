import '../models/articles_model.dart';

/// ONLY class allowed to talk to the remote API / Firestore.
abstract class ArticlesRemoteDataSource {
  Future<List<ArticlesModel>> getAll();
  Future<ArticlesModel> getById(String id);
  Future<ArticlesModel> create(ArticlesModel model);
}

class ArticlesRemoteDataSourceImpl implements ArticlesRemoteDataSource {
  // TODO: inject HTTP client or Firestore instance

  @override
  Future<List<ArticlesModel>> getAll() async {
    // TODO: implement
    throw UnimplementedError();
  }

  @override
  Future<ArticlesModel> getById(String id) async {
    throw UnimplementedError();
  }

  @override
  Future<ArticlesModel> create(ArticlesModel model) async {
    throw UnimplementedError();
  }
}
