import '../entities/articles_entity.dart';
import '../../../../core/resources/data_state.dart';

/// Contract fulfilled by the Data Layer.
/// Domain layer only knows this interface.
abstract class ArticlesRepository {
  Future<DataState<List<ArticlesEntity>>> getAll();
  Future<DataState<ArticlesEntity>> getById(String id);
  Future<DataState<ArticlesEntity>> create(ArticlesEntity entity);
}
