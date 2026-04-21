import '../../domain/entities/auth_entity.dart';

/// Extends [AuthEntity] to handle JSON / Firestore parsing.
/// Never used directly outside the data layer.
class AuthModel extends AuthEntity {
  const AuthModel({required super.id});

  factory AuthModel.fromJson(Map<String, dynamic> json) {
    return AuthModel(id: json['id'] as String);
  }

  Map<String, dynamic> toJson() {
    return {'id': id};
  }
}
