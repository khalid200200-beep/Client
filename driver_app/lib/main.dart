import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'state/driver_state.dart';
import 'theme/driver_theme.dart';
import 'views/auth/driver_login_view.dart';
import 'views/driver_home_view.dart';
import 'views/driver_wallet_view.dart';
import 'views/driver_profile_view.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    ChangeNotifierProvider(
      create: (_) => DriverState(),
      child: const ShippingDriverApp(),
    ),
  );
}

class ShippingDriverApp extends StatelessWidget {
  const ShippingDriverApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'سودرا كابتن',
      debugShowCheckedModeBanner: false,
      theme: DriverTheme.lightTheme,
      locale: const Locale('ar', 'SA'),
      supportedLocales: const [
        Locale('ar', 'SA'),
        Locale('en', 'US'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      // يبدأ التطبيق بشاشة تسجيل دخول الكابتن
      home: const DriverLoginView(),
    );
  }
}

class DriverMainWrapper extends StatefulWidget {
  const DriverMainWrapper({super.key});

  @override
  State<DriverMainWrapper> createState() => _DriverMainWrapperState();
}

class _DriverMainWrapperState extends State<DriverMainWrapper> {
  int _tabIndex = 0;

  @override
  Widget build(BuildContext context) {
    final screens = [
      const DriverHomeView(),
      const DriverWalletView(),
      const DriverProfileView(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _tabIndex,
        children: screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tabIndex,
        onDestinationSelected: (i) => setState(() => _tabIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.local_shipping_outlined), selectedIcon: Icon(Icons.local_shipping), label: 'الطلبات المتاحة'),
          NavigationDestination(icon: Icon(Icons.history_rounded), label: 'المحفظة والسجل'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'حساب الكابتن'),
        ],
      ),
    );
  }
}
