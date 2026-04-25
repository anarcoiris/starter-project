import 'package:news_app_clean_architecture/core/usecase/usecase.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/article_repository.dart';
import 'package:news_app_clean_architecture/core/resources/data_state.dart';

class GenerateDailyNewspaperUseCase implements UseCase<DataState<String>, void> {
  final ArticleRepository _articleRepository;

  GenerateDailyNewspaperUseCase(this._articleRepository);

  @override
  Future<DataState<String>> call({void params}) {
    return _articleRepository.generateDailyNewspaper();
  }
}
