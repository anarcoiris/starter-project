import 'package:news_app_clean_architecture/features/daily_news/domain/entities/article.dart';

abstract class RemoteArticlesEvent {
  const RemoteArticlesEvent();
}

class GetArticles extends RemoteArticlesEvent {
  const GetArticles();
}

class PostArticle extends RemoteArticlesEvent {
  final ArticleEntity article;
  const PostArticle(this.article);
}