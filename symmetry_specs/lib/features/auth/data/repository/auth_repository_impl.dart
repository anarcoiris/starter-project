import '../../../../core/resources/data_state.dart';
import '../../domain/entities/auth_entity.dart';
import '../../domain/repository/auth_repository.dart';
import '../data_sources/auth_remote_data_source.dart';
import '../models/auth_model.dart';

/// Concrete implementation of [AuthRepository].
/// The presentation layer never imports this class.
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;

  const AuthRepositoryImpl(this._remoteDataSource);

  @override
  Future<DataState<List<AuthEntity>>> getAll() async {
    try {
      final models = await _remoteDataSource.getAll();
      return DataSuccess(models);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }

  @override
  Future<DataState<AuthEntity>> getById(String id) async {
    try {
      final model = await _remoteDataSource.getById(id);
      return DataSuccess(model);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }

  @override
  Future<DataState<AuthEntity>> create(AuthEntity entity) async {
    try {
      final model = AuthModel(id: entity.id);
      final result = await _remoteDataSource.create(model);
      return DataSuccess(result);
    } catch (e) {
      return DataFailed(e.toString());
    }
  }
}
