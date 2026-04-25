import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_sign_in/google_sign_in.dart';
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
  Stream<UserEntity?> getUserProfile(String uid) {
    return FirebaseFirestore.instance.collection('users').doc(uid).snapshots().map((snapshot) {
      final data = snapshot.data();
      if (data == null) return null;
      
      return UserEntity(
        uid: uid,
        email: data['email'],
        displayName: data['displayName'],
        photoUrl: data['photoUrl'],
        bio: data['bio'],
        reputationScore: (data['reputation'] as num?)?.toInt() ?? 0,
        isVerified: data['isVerified'] ?? false,
      );
    });
  }

  @override
  Future<UserEntity?> getPublicProfile(String uid) async {
    final doc = await FirebaseFirestore.instance.collection('users').doc(uid).get();
    final data = doc.data();
    if (data == null) return null;

    return UserEntity(
      uid: uid,
      email: data['email'],
      displayName: data['displayName'],
      photoUrl: data['photoUrl'],
      bio: data['bio'],
      reputationScore: (data['reputation'] as num?)?.toInt() ?? 0,
      isVerified: data['isVerified'] ?? false,
    );
  }

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
    final user = credential.user;
    if (displayName != null) {
      await user?.updateDisplayName(displayName);
    }
    
    if (user != null) {
      await FirebaseFirestore.instance.collection('users').doc(user.uid).set({
        'email': user.email,
        'displayName': displayName,
        'createdAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    }
    
    return _mapFirebaseUser(user);
  }

  @override
  Future<UserEntity?> signInWithGoogle() async {
    final googleSignIn = GoogleSignIn();
    final googleUser = await googleSignIn.signIn();
    
    if (googleUser == null) return null;

    final googleAuth = await googleUser.authentication;
    final AuthCredential credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );

    final userCredential = await _firebaseAuth.signInWithCredential(credential);
    final user = userCredential.user;
    
    if (user != null) {
      await FirebaseFirestore.instance.collection('users').doc(user.uid).set({
        'email': user.email,
        'displayName': user.displayName ?? googleUser.displayName,
        'photoUrl': user.photoURL ?? googleUser.photoUrl,
        'lastLoginAt': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    }
    
    return _mapFirebaseUser(user);
  }

  @override
  Future<void> logout() async {
    await _firebaseAuth.signOut();
  }

  @override
  Future<void> updateUserProfile({String? displayName, String? bio, String? photoUrl}) async {
    final user = _firebaseAuth.currentUser;
    if (user != null) {
      if (displayName != null) await user.updateDisplayName(displayName);
      if (photoUrl != null) await user.updatePhotoURL(photoUrl);
      
      // Save bio to Firestore
      if (bio != null) {
        await FirebaseFirestore.instance.collection('users').doc(user.uid).set({
          'bio': bio,
          'updatedAt': FieldValue.serverTimestamp(),
        }, SetOptions(merge: true));
      }
    }
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
