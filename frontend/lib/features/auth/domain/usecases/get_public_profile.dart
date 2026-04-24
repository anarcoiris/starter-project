import 'package:news_app_clean_architecture/core/resources/data_state.dart';
import 'package:news_app_clean_architecture/core/usecases/usecase.dart';
import 'package:news_app_clean_architecture/features/auth/domain/entities/user.dart';
import 'package:news_app_clean_architecture/features/auth/domain/repository/auth_repository.dart';

class GetPublicProfileUseCase implements UseCase<DataState<UserEntity>, String> {
  final AuthRepository _authRepository;

  GetPublicProfileUseCase(this._authRepository);

  @override
  Future<DataState<UserEntity>> call({String? params}) async {
    try {
      final user = await _authRepository.getPublicProfile(params!);
      if (user != null) {
        return DataSuccess(user);
      } else {
        return const DataFailed("User profile not found");
      }
    } catch (e) {
      return DataFailed(e.toString());
    }
  }
}
