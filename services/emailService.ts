import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || 'smtp.gmail.com',
  port: parseInt(process.env.SMTP_PORT || '587'),
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

export const sendVerificationEmail = async (email: string, token: string) => {
  const verificationUrl = `http://localhost:3000/api/auth/verify-email?token=${token}`;
  
  await transporter.sendMail({
    from: `"Your App" <${process.env.SMTP_USER}>`,
    to: email,
    subject: 'Подтверждение email',
    html: `
    <h2>Подтвердите email</h2>
    <p>перейдите по ссылке для подтверждения email: <a href="${verificationUrl}">${verificationUrl}</a></p>
    `,
  });
};