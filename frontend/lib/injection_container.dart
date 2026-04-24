import 'package:get_it/get_it.dart';

import 'package:news_app_clean_architecture/core/di/core_injection.dart';
import 'package:news_app_clean_architecture/features/auth/di/auth_injection.dart';
import 'package:news_app_clean_architecture/features/daily_news/di/news_injection.dart';

final sl = GetIt.instance;

Future<void> initializeDependencies() async {
  // 1. Initialize Core Dependencies (DB, Network, Firebase)
  await initCoreDependencies(sl);

  // 2. Initialize Features
  initAuthDependencies(sl);
  initDailyNewsDependencies(sl);
}