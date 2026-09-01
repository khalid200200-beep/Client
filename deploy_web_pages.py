import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('84.247.141.162', port=22, username='root', password='KkMm1416', timeout=40)

sftp = ssh.open_sftp()

# 1. Create Next.js /src/app/support/page.tsx
support_next_code = """import React from "react";
import PageHeader from "@/components/layout/PageHeader";
import { generateSeoMetadata } from "@/lib/seo";
import { COMPANY_CONFIG, getWhatsAppLink } from "@/data/company.config";
import ContactForm from "@/features/contact/ContactForm";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MapPin, Phone, Mail, Clock, MessageCircle, HelpCircle, ShieldCheck, Headphones } from "lucide-react";

export const metadata = generateSeoMetadata({
  title: "مركز الدعم والمساعدة | تطبيق سودرا SUDRA Support",
  description: "مركز المساعدة والدعم الفني لتطبيق سودرا للشحن والتوصيل. وسائل التواصل، أرقام الدعم الفني، البريد الإلكتروني، والواتساب.",
  path: "/support",
});

export default function SupportPage() {
  const whatsappUrl = getWhatsAppLink();

  return (
    <div className="flex flex-col w-full pb-24" dir="rtl">
      <PageHeader
        badge="الدعم والمساعدة"
        title="مركز الدعم الفني وخدمة العملاء - سودرا"
        subtitle="فريق دعم سودرا متاح على مدار الساعة لمساعدتكم في كل ما يخص طلبات الشحن وتطبيق العملاء وتطبيق الكابتن."
        breadcrumb={[{ label: "الدعم الفني" }]}
      />

      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          {/* Quick Contact Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card variant="glass" className="p-6 bg-white border-slate-200 shadow-md text-right space-y-3">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-600 mb-2">
                <MessageCircle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">المحادثة الفورية (WhatsApp)</h3>
              <p className="text-xs text-slate-600">تواصل فوري ومباشر مع ممثلي خدمة العملاء لخدمة سريعة.</p>
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block mt-2 text-xs font-bold text-emerald-600 hover:text-emerald-700 underline"
              >
                فتح محادثة واتساب الآن &larr;
              </a>
            </Card>

            <Card variant="glass" className="p-6 bg-white border-slate-200 shadow-md text-right space-y-3">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600 mb-2">
                <Mail className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">البريد الإلكتروني للدعم</h3>
              <p className="text-xs text-slate-600">للاستفسارات الرسمية والشكاوى ومتابعة الشحنات التجارية.</p>
              <a
                href="mailto:support@sudra.sa"
                className="inline-block mt-2 text-xs font-bold text-blue-600 hover:text-blue-700 underline font-mono"
              >
                support@sudra.sa
              </a>
            </Card>

            <Card variant="glass" className="p-6 bg-white border-slate-200 shadow-md text-right space-y-3">
              <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600 mb-2">
                <Headphones className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">الاتصال المباشر</h3>
              <p className="text-xs text-slate-600">أوقات العمل: من السبت إلى الخميس (8:00 ص - 10:00 م).</p>
              <a
                href="tel:0551122334"
                className="inline-block mt-2 text-xs font-bold text-amber-600 hover:text-amber-700 underline font-mono"
              >
                0551122334
              </a>
            </Card>
          </div>

          {/* Form & Info Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
            <div className="lg:col-span-7">
              <div className="bg-white p-8 rounded-2xl shadow-xl border border-slate-200">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">إرسال تذكرة دعم فني</h2>
                <p className="text-xs text-slate-600 mb-6">املأ النموذج وسيقوم فريق العمليات بالرد عليك خلال أقل من ساعتين.</p>
                <ContactForm />
              </div>
            </div>

            <div className="lg:col-span-5 space-y-6 text-right">
              <Card variant="glass" className="p-6 bg-white border-slate-200 shadow-xl space-y-4">
                <div className="flex items-center justify-between">
                  <Badge variant="aviation">الأسئلة الشائعة</Badge>
                  <HelpCircle className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="space-y-3 text-xs text-slate-700">
                  <div>
                    <span className="font-bold text-slate-900 block">كيف يمكنني تتبع شحنتي؟</span>
                    <p className="text-slate-600 mt-0.5">من خلال قائمة "شحناتي" داخل التطبيق أو إدخال رقم الشحنة في صفحة التتبع.</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-900 block">كيف أنضم ككابتن توصيل في سودرا؟</span>
                    <p className="text-slate-600 mt-0.5">قم بتحميل تطبيق "سودرا كابتن" وسجل بياناتك ورقم اللوحة، وستتم مراجعة الحساب وتفعيله.</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-900 block">كيف أقوم بحذف حسابي وبياناتي؟</span>
                    <p className="text-slate-600 mt-0.5">من خلال الدخول إلى "حسابي" ثم الضغط على "حذف الحساب نهائياً" وسيتم مسح البيانات فوراً.</p>
                  </div>
                </div>
              </Card>

              <div className="p-6 rounded-2xl bg-emerald-50 border border-emerald-200 text-right space-y-3 shadow-md">
                <div className="flex items-center gap-2 text-emerald-800 font-bold text-sm">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  <span>ضمان الجودة والأمان</span>
                </div>
                <p className="text-xs text-slate-600">
                  جميع الشحنات تخضع للمراقبة والتأمين لضمان وصولها بأمان وسلامة تامة إلى وجهتها.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
"""

try:
    ssh.exec_command("mkdir -p /www/wwwroot/sudra.sa/src/app/support")
    with sftp.file('/www/wwwroot/sudra.sa/src/app/support/page.tsx', 'w') as f:
        f.write(support_next_code)
    print("✅ Created /www/wwwroot/sudra.sa/src/app/support/page.tsx")
except Exception as e:
    print(f"Error creating support page: {e}")

# 2. Update Next.js /src/app/privacy/page.tsx with comprehensive App Store aligned privacy policy
privacy_next_code = """import React from "react";
import PageHeader from "@/components/layout/PageHeader";
import { generateSeoMetadata } from "@/lib/seo";
import { Card } from "@/components/ui/Card";
import { ShieldCheck, Lock, Eye, Database, Trash2, Smartphone } from "lucide-react";

export const metadata = generateSeoMetadata({
  title: "سياسة الخصوصية وحماية البيانات | تطبيق سودرا SUDRA Privacy Policy",
  description: "سياسة الخصوصية لتطبيق سودرا للعملاء وتطبيق سودرا كابتن للسائقين. الشفافية الكاملة في جمع البيانات والامتثال لمعايير Apple App Store.",
  path: "/privacy",
});

export default function PrivacyPage() {
  return (
    <div className="flex flex-col w-full pb-24" dir="rtl">
      <PageHeader
        badge="الخصوصية والأمان"
        title="سياسة الخصوصية وحماية بيانات المستخدمين"
        subtitle="نلتزم بأعلى معايير حماية البيانات والخصوصية وفق اشتراطات Apple App Store والأنظمة المعتمدة."
        breadcrumb={[{ label: "سياسة الخصوصية" }]}
      />

      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 text-right leading-relaxed">
          <Card variant="glass" className="p-8 sm:p-10 space-y-6 text-slate-700 bg-white border-slate-200 shadow-xl">
            <div className="border-b border-slate-100 pb-4">
              <span className="text-xs font-bold text-emerald-600">آخر تحديث: 31 أغسطس 2026</span>
              <h2 className="text-2xl font-black text-slate-900 mt-1">سياسة الخصوصية لتطبيقات منصة سودرا (SUDRA)</h2>
              <p className="text-xs text-slate-500 mt-1">تغطي هذه السياسة تطبيق العميل (SUDRA Client App) وتطبيق السائق (SUDRA Captain App) والموقع الإلكتروني.</p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Database className="w-5 h-5 text-emerald-600" />
                1. البيانات التي نجمعها والأغراض التشغيلية
              </h3>
              <p className="text-sm text-slate-600">
                نجمع فقط البيانات الضرورية لتشغيل خدمة الشحن والتوصيل وضمان أمان الشحنات والمستخدمين:
              </p>
              <ul className="list-disc list-inside space-y-2 text-sm text-slate-600 pr-2">
                <li><strong className="text-slate-900">بيانات الحساب والتواصل:</strong> الاسم، رقم الجوال، والبريد الإلكتروني؛ لإنشاء الحساب، وإرسال رموز التحقق لمرة واحدة (OTP)، واستعادة كلمة المرور، والتنسيق لاستلام وتسليم الشحنة.</li>
                <li><strong className="text-slate-900">الصور ومحتوى الشحنة:</strong> يتيح تطبيق العميل التقاط وإرفاق حتى 5 صور للطرود لتوثيق حالة الشحنة وسلامتها قبل وبعد الاستلام.</li>
                <li><strong className="text-slate-900">الموقع الجغرافي (Location):</strong>
                  <ul className="list-circle list-inside pr-4 space-y-1 mt-1">
                    <li><strong>تطبيق العميل:</strong> تحديد المدينة والمنطقة لتوجيه الطلب للسائقين المتاحين في نفس المنطقة.</li>
                    <li><strong>تطبيق السائق (كابتن سودرا):</strong> إذن الموقع الجغرافي أثناء الاستخدام لتوجيه مسار التوصيل للعميل وتحديث حالة الطلب.</li>
                  </ul>
                </li>
                <li><strong className="text-slate-900">معرفات الجلسة والأجهزة:</strong> رموز جلسة مشفرة (Session Tokens) ومفاتيح أمان مخزنة في iOS Keychain لإبقاء تسجيل الدخول آمناً.</li>
                <li><strong className="text-slate-900">بيانات المركبة (للسائقين فقط):</strong> رقم اللوحة ونوع المركبة للتحقق من هوية الكابتن قبل الاعتماد.</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Lock className="w-5 h-5 text-emerald-600" />
                2. حماية البيانات والتشفير
              </h3>
              <p className="text-sm text-slate-600">
                يتم نقل وتشفير جميع الاتصالات عبر بروتوكول HTTPS/TLS 1.3 الآمن، وتُخزن كلمات المرور باستخدام خوارزميات التشفير القياسية (Bcrypt)، ويتم حفظ التوكنز بأمان داخل iOS Keychain.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Eye className="w-5 h-5 text-emerald-600" />
                3. عدم التتبع وعدم بيع البيانات (No Third-Party Tracking)
              </h3>
              <p className="text-sm text-slate-600">
                نؤكد التزامنا التام بعدم بيع أو تأجير أو مشاركة بيانات المستخدمين مع أي جهات إعلانية أو شبكات تتبع تابعة لجهات خارجية لأغراض التسويق أو التتبع عبر التطبيقات الأخرى.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Trash2 className="w-5 h-5 text-red-600" />
                4. خيار وحق حذف الحساب والبيانات (Account Deletion)
              </h3>
              <p className="text-sm text-slate-600">
                وفقاً لإرشادات Apple App Store (Guideline 5.1.1(v))، يتيح التطبيق خياراً مباشراً لحذف الحساب نهائياً من داخل شاشة "الملف الشخصي" (Profile). عند طلب الحذف، يتم إخفاء ومسح الهوية الشخصية والبيانات المرتبطة فوراً من النظام.
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-emerald-600" />
                5. قنوات التواصل ومسؤول حماية البيانات
              </h3>
              <p className="text-sm text-slate-600">
                لأي استفسار حول سياسة الخصوصية أو ممارسة حقوقك في البيانات:
              </p>
              <div className="bg-slate-50 p-4 rounded-xl text-xs space-y-1 font-mono">
                <div>البريد الإلكتروني: <a href="mailto:privacy@sudra.sa" className="text-emerald-600 underline">privacy@sudra.sa</a> أو <a href="mailto:support@sudra.sa" className="text-emerald-600 underline">support@sudra.sa</a></div>
                <div>الموقع الإلكتروني: <a href="https://sudra.sa" className="text-emerald-600 underline">https://sudra.sa</a></div>
                <div>مركز الدعم: <a href="https://sudra.sa/support" className="text-emerald-600 underline">https://sudra.sa/support</a></div>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
"""

with sftp.file('/www/wwwroot/sudra.sa/src/app/privacy/page.tsx', 'w') as f:
    f.write(privacy_next_code)
print("✅ Updated /www/wwwroot/sudra.sa/src/app/privacy/page.tsx")

sftp.close()
ssh.close()
