import 'package:flutter_bloc/flutter_bloc.dart';

import '../../domain/entities/articles_entity.dart';
import '../../domain/use_cases/get_articles_use_case.dart';
import 'articles_state.dart';
import '../../../../core/usecase/usecase.dart';

/// Presentation state manager for the Articles feature.
/// ONLY imports use cases — never repositories or data sources.
class ArticlesCubit extends Cubit<ArticlesState> {
  final GetArticlesUseCase _getArticles;

  ArticlesCubit({required GetArticlesUseCase getArticles})
      : _getArticles = getArticles,
        super(const ArticlesInitial());

  Future<void> loadArticles() async {
    emit(const ArticlesLoading());
    final result = await _getArticles(const NoParams());
    result.data != null
        ? emit(ArticlesLoaded(result.data!))
        : emit(ArticlesError(result.error ?? 'Unknown error'));
  }
}
