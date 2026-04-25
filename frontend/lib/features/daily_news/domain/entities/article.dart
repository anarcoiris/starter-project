import 'package:equatable/equatable.dart';

class ArticleEntity extends Equatable{
  final String ? articleId;
  final String ? author;
  final String ? authorId;
  final String ? title;
  final String ? description;
  final String ? url;
  final String ? urlToImage;
  final String ? publishedAt;
  final String ? content;
  final double ? tokensEarned;
  final String ? source;
  final String ? pdfPath;
  final int ? upvotes;
  final int ? downvotes;

  const ArticleEntity({
    this.articleId,
    this.author,
    this.authorId,
    this.title,
    this.description,
    this.url,
    this.urlToImage,
    this.publishedAt,
    this.content,
    this.tokensEarned,
    this.source,
    this.pdfPath,
    this.upvotes,
    this.downvotes,
  });


  @override
  List < Object ? > get props {
    return [
      articleId,
      author,
      authorId,
      title,
      description,
      url,
      urlToImage,
      publishedAt,
      content,
      tokensEarned,
      source,
      pdfPath,
      upvotes,
      downvotes,
    ];
  }
}