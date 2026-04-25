import 'package:get_it/get_it.dart';

import 'package:news_app_clean_architecture/core/core.dart';
import 'package:news_app_clean_architecture/features/auth/auth.dart';
import 'package:news_app_clean_architecture/features/auth/domain/usecases/get_public_profile.dart';

void initAuthDependencies(GetIt sl) {
  // Analytics
  sl.registerSingleton<AnalyticsRepository>(FirestoreAnalyticsImpl(sl(), sl()));

  // Auth Repositories
  sl.registerSingleton<AuthRepository>(AuthRepositoryImpl(sl()));
  
  // Auth UseCases
  sl.registerSingleton<GetPublicProfileUseCase>(
    GetPublicProfileUseCase(sl())
  );

  // Auth Blocs
  sl.registerLazySingleton<AuthCubit>(() => AuthCubit(sl()));
}
