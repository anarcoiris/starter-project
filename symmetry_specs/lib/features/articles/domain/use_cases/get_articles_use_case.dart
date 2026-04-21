import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/articles_entity.dart';
import '../repository/articles_repository.dart';

/// Retrieves the full list of articles.
class GetArticlesUseCase implements UseCase<List<ArticlesEntity>, NoParams> {
  final ArticlesRepository _repository;

  const GetArticlesUseCase(this._repository);

  @override
  Future<DataState<List<ArticlesEntity>>> call(NoParams params) {
    return _repository.getAll();
  }
}
