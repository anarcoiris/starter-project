import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/articles_entity.dart';
import '../repository/articles_repository.dart';

class GetArticlesByIdParams {
  final String id;
  const GetArticlesByIdParams(this.id);
}

class GetArticlesByIdUseCase implements UseCase<ArticlesEntity, GetArticlesByIdParams> {
  final ArticlesRepository _repository;

  const GetArticlesByIdUseCase(this._repository);

  @override
  Future<DataState<ArticlesEntity>> call(GetArticlesByIdParams params) {
    return _repository.getById(params.id);
  }
}
