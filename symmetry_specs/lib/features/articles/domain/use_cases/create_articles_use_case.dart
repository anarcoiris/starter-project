import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/articles_entity.dart';
import '../repository/articles_repository.dart';

class CreateArticlesUseCase implements UseCase<ArticlesEntity, ArticlesEntity> {
  final ArticlesRepository _repository;

  const CreateArticlesUseCase(this._repository);

  @override
  Future<DataState<ArticlesEntity>> call(ArticlesEntity params) {
    return _repository.create(params);
  }
}
