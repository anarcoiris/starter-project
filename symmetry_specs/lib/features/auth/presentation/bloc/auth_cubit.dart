import 'package:flutter_bloc/flutter_bloc.dart';

import '../../domain/entities/auth_entity.dart';
import '../../domain/use_cases/get_auths_use_case.dart';
import 'auth_state.dart';
import '../../../../core/usecase/usecase.dart';

/// Presentation state manager for the Auth feature.
/// ONLY imports use cases — never repositories or data sources.
class AuthCubit extends Cubit<AuthState> {
  final GetAuthsUseCase _getAuths;

  AuthCubit({required GetAuthsUseCase getAuths})
      : _getAuths = getAuths,
        super(const AuthInitial());

  Future<void> loadAuths() async {
    emit(const AuthLoading());
    final result = await _getAuths(const NoParams());
    result.data != null
        ? emit(AuthLoaded(result.data!))
        : emit(AuthError(result.error ?? 'Unknown error'));
  }
}
