import 'package:firebase_auth/firebase_auth.dart';
import 'package:news_app_clean_architecture/features/auth/domain/entities/user.dart';
import 'package:news_app_clean_architecture/features/auth/domain/repository/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final FirebaseAuth _firebaseAuth;

  AuthRepositoryImpl(this._firebaseAuth);

  @override
  Stream<UserEntity?> get onAuthStateChanged => _firebaseAuth.authStateChanges().map(_mapFirebaseUser);

  @override
  UserEntity? get currentUser => _mapFirebaseUser(_firebaseAuth.currentUser);

  @override
  Future<UserEntity?> login({required String email, required String password}) async {
    final credential = await _firebaseAuth.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
    return _mapFirebaseUser(credential.user);
  }

  @override
  Future<UserEntity?> register({required String email, required String password, String? displayName}) async {
    final credential = await _firebaseAuth.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    if (displayName != null) {
      await credential.user?.updateDisplayName(displayName);
    }
    return _mapFirebaseUser(credential.user);
  }

  @override
  Future<void> logout() async {
    await _firebaseAuth.signOut();
  }

  UserEntity? _mapFirebaseUser(User? user) {
    if (user == null) return null;
    return UserEntity(
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoUrl: user.photoURL,
    );
  }
}
