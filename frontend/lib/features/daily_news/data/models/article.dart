import 'package:floor/floor.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/entities/article.dart';
import 'package:news_app_clean_architecture/core/constants/constants.dart';

@Entity(tableName: 'article', primaryKeys: ['articleId'])
class ArticleModel extends ArticleEntity {
  const ArticleModel({
    String? articleId,
    String? author,
    String? authorId,
    String? title,
    String? description,
    String? url,
    String? urlToImage,
    String? publishedAt,
    String? content,
    double? tokensEarned,
    String? source,
    String? pdfPath,
    int? upvotes,
    int? downvotes,
  }) : super(
          articleId: articleId,
          author: author,
          authorId: authorId,
          title: title,
          description: description,
          url: url,
          urlToImage: urlToImage,
          publishedAt: publishedAt,
          content: content,
          tokensEarned: tokensEarned,
          source: source,
          pdfPath: pdfPath,
          upvotes: upvotes,
          downvotes: downvotes,
        );


  factory ArticleModel.fromJson(Map<String, dynamic> map) {
    // Generate articleId if missing
    String? artId = map['articleId'];
    if (artId == null || artId == 'string' || artId.isEmpty) {
       final urlStr = map['url'] ?? '';
       artId = urlStr.isNotEmpty 
          ? urlStr.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '_')
          : (map['title'] ?? 'unknown').replaceAll(RegExp(r'[^a-zA-Z0-9]'), '_').toLowerCase();
    }

    return ArticleModel(
      articleId: artId,
      author: map['author'] ?? "",
      authorId: map['authorId'],
      title: map['title'] ?? "",
      description: map['description'] ?? "",
      url: map['url'] ?? "",
      urlToImage: map['urlToImage'] != null && map['urlToImage'] != ""
          ? map['urlToImage']
          : kDefaultImage,
      publishedAt: map['publishedAt'] ?? "",
      content: map['content'] ?? "",
      tokensEarned: (map['tokensEarned'] as num?)?.toDouble() ?? 0.0,
      source: map['source'] ?? "SYMMETRY NEWS",
      pdfPath: map['pdfPath'],
      upvotes: map['upvotes'] ?? 0,
      downvotes: map['downvotes'] ?? 0,
    );
  }

  factory ArticleModel.fromRawData(Map<String, dynamic> map) => ArticleModel.fromJson(map);

  ArticleEntity toEntity() => ArticleEntity(
        articleId: articleId,
        author: author,
        authorId: authorId,
        title: title,
        description: description,
        url: url,
        urlToImage: urlToImage,
        publishedAt: publishedAt,
        content: content,
        tokensEarned: tokensEarned,
        source: source,
        pdfPath: pdfPath,
        upvotes: upvotes,
        downvotes: downvotes,
      );


  factory ArticleModel.fromEntity(ArticleEntity entity) {
    return ArticleModel(
        articleId: entity.articleId,
        author: entity.author,
        authorId: entity.authorId,
        title: entity.title,
        description: entity.description,
        url: entity.url,
        urlToImage: entity.urlToImage,
        publishedAt: entity.publishedAt,
        content: entity.content,
        tokensEarned: entity.tokensEarned,
        source: entity.source,
        pdfPath: entity.pdfPath,
        upvotes: entity.upvotes,
        downvotes: entity.downvotes);
  }


  Map<String, dynamic> toJson() {
    return {
      'articleId': articleId,
      'author': author ?? "",
      'authorId': authorId,
      'title': title ?? "",
      'description': description ?? "",
      'url': url ?? "",
      'urlToImage': urlToImage ?? "",
      'publishedAt': publishedAt ?? DateTime.now().toIso8601String(),
      'content': content ?? "",
      'source': 'Symmetry Journalist',
      'category': 'general',
      'upvotes': upvotes ?? 0,
      'downvotes': downvotes ?? 0,
    };
  }

  Map<String, dynamic> toRawData() => toJson();
}
