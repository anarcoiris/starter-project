import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/auth_entity.dart';
import '../repository/auth_repository.dart';

/// Retrieves the full list of auths.
class GetAuthsUseCase implements UseCase<List<AuthEntity>, NoParams> {
  final AuthRepository _repository;

  const GetAuthsUseCase(this._repository);

  @override
  Future<DataState<List<AuthEntity>>> call(NoParams params) {
    return _repository.getAll();
  }
}
