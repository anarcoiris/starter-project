import '../../../../core/resources/data_state.dart';
import '../../domain/entities/articles_entity.dart';
import '../../domain/repository/articles_repository.dart';
import '../data_sources/articles_remote_data_source.dart';
import '../models/articles_model.dart';

/// Concrete implementation of [ArticlesRepository].
/// The presentation layer never imports this class.
class ArticlesRepositoryImpl implements ArticlesRepository {
  final ArticlesRemoteDataSource _remoteDataSource;

  const ArticlesRepositoryImpl(this._remoteDataSource);

  @override
  Future<DataState<List<ArticlesEntity>>> getAll() async {
    try {
      final models = await _remoteDataSource.getAll();
      return DataSuccess(models);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }

  @override
  Future<DataState<ArticlesEntity>> getById(String id) async {
    try {
      final model = await _remoteDataSource.getById(id);
      return DataSuccess(model);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }

  @override
  Future<DataState<ArticlesEntity>> create(ArticlesEntity entity) async {
    try {
      final model = ArticlesModel(id: entity.id);
      final result = await _remoteDataSource.create(model);
      return DataSuccess(result);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }
}
