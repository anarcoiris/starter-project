import '../../domain/entities/articles_entity.dart';

/// Extends [ArticlesEntity] to handle JSON / Firestore parsing.
/// Never used directly outside the data layer.
class ArticlesModel extends ArticlesEntity {
  const ArticlesModel({required super.id});

  factory ArticlesModel.fromJson(Map<String, dynamic> json) {
    return ArticlesModel(id: json['id'] as String);
  }

  Map<String, dynamic> toJson() {
    return {'id': id};
  }
}
