import 'package:get_it/get_it.dart';

import 'package:news_app_clean_architecture/features/daily_news/domain/daily_news_domain.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/daily_news_presentation.dart';
import 'package:news_app_clean_architecture/features/daily_news/presentation/bloc/reward/reward_cubit.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/firebase_data_source.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/chat_service.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/news_api_service.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/data_sources/remote/reward_api_service.dart';
import 'package:news_app_clean_architecture/features/daily_news/domain/repository/storage_repository.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/repository/article_repository_impl.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/repository/reward_repository_impl.dart';
import 'package:news_app_clean_architecture/features/daily_news/data/repository/storage_repository_impl.dart';

void initDailyNewsDependencies(GetIt sl) {
  // Data Sources
  sl.registerSingleton<FirebaseDataSource>(FirebaseDataSource(sl()));
  sl.registerSingleton<NewsApiService>(NewsApiService(sl(instanceName: 'backend')));
  sl.registerSingleton<ChatService>(ChatService(sl(instanceName: 'backend')));
  sl.registerSingleton<RewardApiService>(RewardApiService(sl(instanceName: 'backend')));

  // Repositories
  sl.registerSingleton<StorageRepository>(StorageRepositoryImpl(sl()));
  sl.registerSingleton<RewardRepository>(RewardRepositoryImpl(sl()));
  sl.registerSingleton<ArticleRepository>(
    ArticleRepositoryImpl(sl(), sl(), sl())
  );

  // UseCases
  sl.registerSingleton<GetArticleUseCase>(GetArticleUseCase(sl()));
  sl.registerSingleton<PostArticleUseCase>(PostArticleUseCase(sl()));
  sl.registerSingleton<GetSavedArticleUseCase>(GetSavedArticleUseCase(sl()));
  sl.registerSingleton<SaveArticleUseCase>(SaveArticleUseCase(sl()));
  sl.registerSingleton<RemoveArticleUseCase>(RemoveArticleUseCase(sl()));
  sl.registerSingleton<ClaimRewardUseCase>(ClaimRewardUseCase(sl()));
  sl.registerSingleton<GetBalanceUseCase>(GetBalanceUseCase(sl()));
  sl.registerSingleton<UploadImageUseCase>(UploadImageUseCase(sl()));

  // Blocs
  sl.registerFactory<RemoteArticlesBloc>(
    ()=> RemoteArticlesBloc(sl(), sl())
  );

  sl.registerFactory<LocalArticleBloc>(
    ()=> LocalArticleBloc(sl(), sl(), sl())
  );

  sl.registerFactory<ChatBloc>(
    () => ChatBloc(sl(), sl())
  );

  sl.registerFactory<RewardCubit>(
    () => RewardCubit(sl(), sl())
  );
}
