import axios from "axios";

export const sendVerificationEmail = async (email: string, token: string) => {
  const verificationUrl = `https://server-from-project-react-native.onrender.com/api/auth/verify-email?token=${token}`;

 console.log("📧 Attempting to send email to:", email);
  console.log("📧 MAILERSEND_FROM:", process.env.MAILERSEND_FROM);
  console.log("📧 API Key exists:", !!process.env.MAILERSEND_API_KEY);

  await axios.post(
    "https://api.mailersend.com/v1/messages",
    {
      from: { email: process.env.MAILERSEND_FROM },
      to: [{ email }],
      subject: "Подтверждение email",
      html: `
        <h2>Подтвердите email</h2>
        <p>Перейдите по ссылке для подтверждения email:</p>
        <a href="${verificationUrl}">${verificationUrl}</a>
      `,
    },
    { 
      headers: {
        Authorization: `Bearer ${process.env.MAILERSEND_API_KEY}`,
        "Content-Type": "application/json",
      },
    }
  );
};

