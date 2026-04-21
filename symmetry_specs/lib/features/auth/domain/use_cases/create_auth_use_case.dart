import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/auth_entity.dart';
import '../repository/auth_repository.dart';

class CreateAuthUseCase implements UseCase<AuthEntity, AuthEntity> {
  final AuthRepository _repository;

  const CreateAuthUseCase(this._repository);

  @override
  Future<DataState<AuthEntity>> call(AuthEntity params) {
    return _repository.create(params);
  }
}
