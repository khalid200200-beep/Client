import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../state/client_state.dart';
import '../../theme/app_theme.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/custom_text_field.dart';

class CreateOrderView extends StatefulWidget {
  const CreateOrderView({super.key});

  @override
  State<CreateOrderView> createState() => _CreateOrderViewState();
}

class _CreateOrderViewState extends State<CreateOrderView> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _phoneController;
  late TextEditingController _cityController;
  final TextEditingController _notesController = TextEditingController();
  int _packageCount = 1;

  final List<File> _selectedImageFiles = [];
  final List<String> _imagesBase64 = [];
  final ImagePicker _picker = ImagePicker();
  static const int _maxImages = 5;

  @override
  void initState() {
    super.initState();
    final clientState = Provider.of<ClientState>(context, listen: false);
    _phoneController = TextEditingController(text: clientState.currentUser.phone);
    _cityController = TextEditingController(
      text: clientState.currentUser.city.isNotEmpty ? clientState.currentUser.city : 'الخرطوم',
    );
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _cityController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  /// التقاط صورة بالكاميرا
  Future<void> _pickFromCamera() async {
    if (_selectedImageFiles.length >= _maxImages) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('الحد الأقصى المسموح به هو 5 صور للشحنة')),
      );
      return;
    }

    try {
      final pickedFile = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 75,
      );

      if (pickedFile != null) {
        final bytes = await pickedFile.readAsBytes();
        final base64String = 'data:image/jpeg;base64,${base64Encode(bytes)}';
        setState(() {
          _selectedImageFiles.add(File(pickedFile.path));
          _imagesBase64.add(base64String);
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تعذر التقاط الصورة: $e')),
        );
      }
    }
  }

  /// اختيار صور متعددة من المعرض
  Future<void> _pickFromGallery() async {
    final remainingSlots = _maxImages - _selectedImageFiles.length;
    if (remainingSlots <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('الحد الأقصى المسموح به هو 5 صور للشحنة')),
      );
      return;
    }

    try {
      final pickedFiles = await _picker.pickMultiImage(
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 75,
      );

      if (pickedFiles.isNotEmpty) {
        final filesToAdd = pickedFiles.take(remainingSlots).toList();
        for (final pickedFile in filesToAdd) {
          final bytes = await pickedFile.readAsBytes();
          final base64String = 'data:image/jpeg;base64,${base64Encode(bytes)}';
          _selectedImageFiles.add(File(pickedFile.path));
          _imagesBase64.add(base64String);
        }
        setState(() {});
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تعذر اختيار الصور: $e')),
        );
      }
    }
  }

  void _showImageSourceDialog() {
    if (_selectedImageFiles.length >= _maxImages) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم الوصول للحد الأقصى (5 صور)')),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'إضافة صورة للشحنة (حتى 5 صور)',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: const Icon(Icons.camera_alt_rounded, color: AppTheme.primaryGreen),
                title: const Text('التقاط صورة بالكاميرا 📷'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickFromCamera();
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library_rounded, color: AppTheme.primaryRed),
                title: const Text('اختيار من المعرض 🖼️'),
                subtitle: Text('المتبقي متاح: ${_maxImages - _selectedImageFiles.length} صور'),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickFromGallery();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImageFiles.removeAt(index);
      _imagesBase64.removeAt(index);
    });
  }

  void _previewImage(File file) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
              child: Image.file(file, fit: BoxFit.contain),
            ),
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('إغلاق', style: TextStyle(color: AppTheme.primaryRed, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_packageCount < 1) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('❌ الرجاء تحديد عدد القطع للشحنة (1 قطعة على الأقل)'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (_selectedImageFiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('❌ يرجى إضافة صورة واحدة على الأقل للشحنة (حقل إلزامي) 📷'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final clientState = Provider.of<ClientState>(context, listen: false);
    final cityName = _cityController.text.trim();

    final success = await clientState.createOrder(
      phone: _phoneController.text.trim(),
      city: cityName,
      packageCount: _packageCount,
      notes: _notesController.text.trim(),
      imagePath: _imagesBase64.isNotEmpty ? _imagesBase64.first : null,
      images: _imagesBase64,
    );

    if (!mounted) return;

    if (success) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          title: const Column(
            children: [
              Icon(Icons.check_circle_rounded, color: Colors.green, size: 55),
              SizedBox(height: 12),
              Text('تم إرسال طلب الشحن بنجاح!', textAlign: TextAlign.center, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          content: Text(
            'تم توجيه طلبك فورياً إلى مناديب التوصيل في مدينة $cityName.\nستصلك إشعارات فور قبول الطلب.',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
          ),
          actions: [
            Center(
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen),
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pop(context);
                },
                child: const Text('حسناً', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ فشل إرسال الطلب: ${clientState.errorMessage ?? "حدث خطأ في الخادم"}'),
          backgroundColor: Colors.red.shade700,
          duration: const Duration(seconds: 4),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final clientState = Provider.of<ClientState>(context);

    return Scaffold(
      backgroundColor: AppTheme.scaffoldBackground,
      appBar: AppBar(
        title: const Text('طلب شحن جديد 📦', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 12)],
                  border: Border.all(color: AppTheme.borderColor),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('بيانات التواصل والاستلام', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    CustomTextField(
                      label: 'رقم جوال العميل',
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      prefixIcon: const Icon(Icons.phone_outlined, color: AppTheme.textMuted),
                      validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال رقم الجوال' : null,
                    ),
                    const SizedBox(height: 16),
                    CustomTextField(
                      label: 'مدينة الشحن / الاستلام',
                      hint: 'اكتب اسم المدينة أو الولاية (الخرطوم، الرياض...)',
                      controller: _cityController,
                      prefixIcon: const Icon(Icons.location_city_outlined, color: AppTheme.textMuted),
                      validator: (v) => v == null || v.isEmpty ? 'الرجاء إدخال اسم المدينة' : null,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 12)],
                  border: Border.all(color: AppTheme.borderColor),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('تفاصيل الشحنة', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('عدد القطع والطرود', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                            Text('حدد كمية الطرود أو الصناديق', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppTheme.scaffoldBackground,
                            borderRadius: BorderRadius.circular(30),
                            border: Border.all(color: Colors.grey.shade200),
                          ),
                          child: Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.remove, size: 20, color: AppTheme.primaryGreen),
                                onPressed: () {
                                  if (_packageCount > 1) setState(() => _packageCount--);
                                },
                              ),
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 8),
                                child: Text('$_packageCount', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                              ),
                              IconButton(
                                icon: const Icon(Icons.add, size: 20, color: AppTheme.primaryGreen),
                                onPressed: () => setState(() => _packageCount++),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const Divider(height: 28),

                    // قسم الصور المتعددة
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('صور الشحنة (حتى 5 صور)', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                        Text(
                          '${_selectedImageFiles.length}/$_maxImages',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: _selectedImageFiles.length == _maxImages ? AppTheme.primaryRed : AppTheme.textMuted,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // قائمة الصور المحددة بشكل أفقي + زر إضافة
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          if (_selectedImageFiles.length < _maxImages)
                            GestureDetector(
                              onTap: _showImageSourceDialog,
                              child: Container(
                                width: 90,
                                height: 90,
                                margin: const EdgeInsets.only(left: 10),
                                decoration: BoxDecoration(
                                  color: AppTheme.scaffoldBackground,
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(color: Colors.grey.shade300, style: BorderStyle.solid),
                                ),
                                child: const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.add_a_photo_outlined, size: 28, color: AppTheme.primaryRed),
                                    SizedBox(height: 4),
                                    Text('إضافة صورة', style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600)),
                                  ],
                                ),
                              ),
                            ),
                          ..._selectedImageFiles.asMap().entries.map((entry) {
                            final idx = entry.key;
                            final file = entry.value;
                            return Stack(
                              children: [
                                GestureDetector(
                                  onTap: () => _previewImage(file),
                                  child: Container(
                                    width: 90,
                                    height: 90,
                                    margin: const EdgeInsets.only(left: 10),
                                    decoration: BoxDecoration(
                                      borderRadius: BorderRadius.circular(16),
                                      border: Border.all(color: Colors.green.shade400, width: 1.5),
                                    ),
                                    child: ClipRRect(
                                      borderRadius: BorderRadius.circular(15),
                                      child: Image.file(file, fit: BoxFit.cover),
                                    ),
                                  ),
                                ),
                                Positioned(
                                  top: 4,
                                  left: 14,
                                  child: GestureDetector(
                                    onTap: () => _removeImage(idx),
                                    child: Container(
                                      padding: const EdgeInsets.all(3),
                                      decoration: const BoxDecoration(
                                        color: AppTheme.primaryRed,
                                        shape: BoxShape.circle,
                                      ),
                                      child: const Icon(Icons.close, color: Colors.white, size: 14),
                                    ),
                                  ),
                                ),
                              ],
                            );
                          }),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),
                    CustomTextField(
                      label: 'ملاحظات وتفاصيل الشحنة للمندوب (إلزامي)',
                      hint: 'اكتب تفاصيل الشحنة، العنوان الدقيق، أو أي تعليمات للمندوب',
                      controller: _notesController,
                      maxLines: 3,
                      validator: (v) => (v == null || v.trim().isEmpty) ? 'الرجاء كتابة تفاصيل وملاحظات الشحنة' : null,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              clientState.isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppTheme.primaryRed))
                  : CustomRedButton(
                      text: 'إرسال طلب الشحن إلى أقرب مندوب 🚀',
                      onPressed: _submit,
                      trailingIcon: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
                    ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
