import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:news_app_clean_architecture/features/auth/domain/entities/user.dart';
import 'package:news_app_clean_architecture/features/auth/domain/repository/auth_repository.dart';

abstract class AuthState extends Equatable {
  const AuthState();
  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class Authenticated extends AuthState {
  final UserEntity user;
  const Authenticated(this.user);
  @override
  List<Object?> get props => [user];
}
class Unauthenticated extends AuthState {}
class AuthError extends AuthState {
  final String message;
  const AuthError(this.message);
  @override
  List<Object?> get props => [message];
}

class AuthCubit extends Cubit<AuthState> {
  final AuthRepository _authRepository;
  StreamSubscription<UserEntity?>? _profileSubscription;

  AuthCubit(this._authRepository) : super(AuthInitial()) {
    _authRepository.onAuthStateChanged.listen((user) {
      if (user != null) {
        _subscribeToProfile(user);
      } else {
        _profileSubscription?.cancel();
        emit(Unauthenticated());
      }
    });
  }

  void _subscribeToProfile(UserEntity user) {
    emit(Authenticated(user));
    _profileSubscription?.cancel();
    _profileSubscription = _authRepository.getUserProfile(user.uid).listen((userProfile) {
      if (userProfile != null) {
        emit(Authenticated(userProfile));
      }
    });
  }

  @override
  Future<void> close() {
    _profileSubscription?.cancel();
    return super.close();
  }


  Future<void> login(String email, String password) async {
    try {
      emit(AuthLoading());
      await _authRepository.login(email: email, password: password);
    } catch (e) {
      emit(AuthError(e.toString()));
      emit(Unauthenticated());
    }
  }

  Future<void> register(String email, String password, String displayName) async {
    try {
      emit(AuthLoading());
      await _authRepository.register(email: email, password: password, displayName: displayName);
    } catch (e) {
      emit(AuthError(e.toString()));
      emit(Unauthenticated());
    }
  }

  Future<void> signInWithGoogle() async {
    try {
      emit(AuthLoading());
      await _authRepository.signInWithGoogle();
    } catch (e) {
      emit(AuthError(e.toString()));
      emit(Unauthenticated());
    }
  }

  Future<void> logout() async {
    await _authRepository.logout();
  }

  Future<void> updateBio(String bio) async {
    try {
      await _authRepository.updateUserProfile(bio: bio);
    } catch (e) {
      emit(AuthError(e.toString()));
    }
  }
}
