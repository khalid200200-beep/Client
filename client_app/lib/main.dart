import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'state/client_state.dart';
import 'theme/app_theme.dart';
import 'views/auth/login_view.dart';
import 'views/home/home_view.dart';
import 'views/orders/create_order_view.dart';
import 'views/orders/my_orders_view.dart';
import 'views/profile/profile_view.dart';
import 'widgets/custom_bottom_nav.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    ChangeNotifierProvider(
      create: (_) => ClientState(),
      child: const ShippingClientApp(),
    ),
  );
}

class ShippingClientApp extends StatelessWidget {
  const ShippingClientApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'سودرا',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
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
      // فحص الجلسة والاحتفاظ بتسجيل الدخول التلقائي
      home: const AuthGate(),
    );
  }
}

/// بوابة التحقق من الجلسة المحفوظة تلقائياً
class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _isChecking = true;

  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  Future<void> _checkSession() async {
    final clientState = Provider.of<ClientState>(context, listen: false);
    await clientState.checkExistingSession();
    if (mounted) {
      setState(() => _isChecking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return const Scaffold(
        backgroundColor: AppTheme.scaffoldBackground,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.local_shipping_rounded, size: 60, color: AppTheme.primaryGreen),
              SizedBox(height: 20),
              CircularProgressIndicator(color: AppTheme.primaryGreen),
            ],
          ),
        ),
      );
    }

    final clientState = Provider.of<ClientState>(context);
    if (clientState.isLoggedIn) {
      return const ClientMainWrapper();
    } else {
      return const LoginView();
    }
  }
}

/// الغلاف الرئيسي بعد تسجيل الدخول
class ClientMainWrapper extends StatefulWidget {
  const ClientMainWrapper({super.key});

  @override
  State<ClientMainWrapper> createState() => _ClientMainWrapperState();
}

class _ClientMainWrapperState extends State<ClientMainWrapper> {
  int _tabIndex = 0;

  void _onNewOrderPressed() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const CreateOrderView()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      HomeView(onOpenOrdersTab: () => setState(() => _tabIndex = 1)),
      const MyOrdersView(),
      const Scaffold(
        body: Center(child: Text('لا توجد إشعارات جديدة حالياً', style: TextStyle(color: AppTheme.textMuted))),
      ),
      const ProfileView(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _tabIndex,
        children: screens,
      ),
      bottomNavigationBar: CustomBottomNavBar(
        currentIndex: _tabIndex,
        onTabSelected: (idx) => setState(() => _tabIndex = idx),
        onNewOrderPressed: _onNewOrderPressed,
      ),
    );
  }
}
