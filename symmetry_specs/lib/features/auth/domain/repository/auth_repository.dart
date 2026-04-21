import '../entities/auth_entity.dart';
import '../../../../core/resources/data_state.dart';

/// Contract fulfilled by the Data Layer.
/// Domain layer only knows this interface.
abstract class AuthRepository {
  Future<DataState<List<AuthEntity>>> getAll();
  Future<DataState<AuthEntity>> getById(String id);
  Future<DataState<AuthEntity>> create(AuthEntity entity);
}
