import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class CustomRedButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final Widget? trailingIcon;
  final double height;
  final double? width;
  final bool isGlowing;

  const CustomRedButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.trailingIcon,
    this.height = 54.0,
    this.width,
    this.isGlowing = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width ?? double.infinity,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(height / 2),
        gradient: AppTheme.primaryGradient,
        boxShadow: isGlowing
            ? [
                BoxShadow(
                  color: AppTheme.primaryRed.withOpacity(0.35),
                  blurRadius: 18,
                  offset: const Offset(0, 8),
                  spreadRadius: 2,
                ),
              ]
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(height / 2),
          onTap: onPressed,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  text,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (trailingIcon != null) ...[
                  const SizedBox(width: 10),
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: trailingIcon!,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
