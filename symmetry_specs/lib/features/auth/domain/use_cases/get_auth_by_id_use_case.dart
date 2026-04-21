import '../../../../core/resources/data_state.dart';
import '../../../../core/usecase/usecase.dart';
import '../entities/auth_entity.dart';
import '../repository/auth_repository.dart';

class GetAuthByIdParams {
  final String id;
  const GetAuthByIdParams(this.id);
}

class GetAuthByIdUseCase implements UseCase<AuthEntity, GetAuthByIdParams> {
  final AuthRepository _repository;

  const GetAuthByIdUseCase(this._repository);

  @override
  Future<DataState<AuthEntity>> call(GetAuthByIdParams params) {
    return _repository.getById(params.id);
  }
}
