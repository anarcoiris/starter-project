import 'package:news_app_clean_architecture/core/usecase/usecase.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/article_repository.dart';
import 'package:news_app_clean_architecture/core/resources/data_state.dart';

class VoteArticleUseCase implements UseCase<DataState<void>, VoteParams> {
  final ArticleRepository _articleRepository;

  VoteArticleUseCase(this._articleRepository);

  @override
  Future<DataState<void>> call({VoteParams? params}) {
    return _articleRepository.voteArticle(params!.articleId, params.userId, params.isUpvote);
  }
}

class VoteParams {
  final String articleId;
  final String userId;
  final bool isUpvote;

  VoteParams({required this.articleId, required this.userId, required this.isUpvote});
}
