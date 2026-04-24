import 'package:news_app_clean_architecture/features/auth/domain/entities/user.dart';
import 'package:news_app_clean_architecture/features/auth/domain/repository/auth_repository.dart';

/// Fetches a public user profile by UID.
/// Returns null if the user is not found.
class GetPublicProfileUseCase {
  final AuthRepository _authRepository;

  GetPublicProfileUseCase(this._authRepository);

  Future<UserEntity?> call({String? params}) async {
    if (params == null) return null;
    return _authRepository.getPublicProfile(params);
  }
}
