"""
이미지-텍스트-PDF 변환 및 프린터 출력 프로그램
어르신용 간단한 UI
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import platform

# Windows 프린터 지원
if platform.system() == 'Windows':
    import win32print
    import win32api


class ImageToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사진 PDF 출력기")
        self.root.geometry("900x700")

        # 변수 초기화
        self.image_path = None
        self.image_display = None

        # 한글 폰트 설정 (Windows 기본 폰트)
        self.setup_fonts()

        # UI 구성
        self.create_widgets()

    def setup_fonts(self):
        """한글 폰트 설정"""
        try:
            # Windows 기본 폰트 사용
            if platform.system() == 'Windows':
                font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('korean', font_path))
                    self.pdf_font = 'korean'
                else:
                    self.pdf_font = 'Helvetica'
            else:
                self.pdf_font = 'Helvetica'
        except:
            self.pdf_font = 'Helvetica'

    def create_widgets(self):
        """UI 위젯 생성"""
        # 큰 글씨 스타일
        title_font = ('맑은 고딕', 24, 'bold')
        button_font = ('맑은 고딕', 16, 'bold')
        text_font = ('맑은 고딕', 14)

        # 제목
        title_label = tk.Label(
            self.root,
            text="📸 사진 PDF 출력기",
            font=title_font,
            pady=20
        )
        title_label.pack()

        # 1단계: 사진 선택
        step1_frame = tk.LabelFrame(
            self.root,
            text="1단계: 사진 선택",
            font=text_font,
            padx=20,
            pady=10
        )
        step1_frame.pack(fill="x", padx=20, pady=10)

        self.select_button = tk.Button(
            step1_frame,
            text="📁 사진 선택하기",
            font=button_font,
            command=self.select_image,
            bg="#4CAF50",
            fg="white",
            padx=30,
            pady=15,
            cursor="hand2"
        )
        self.select_button.pack(pady=10)

        # 이미지 미리보기
        self.preview_frame = tk.Frame(step1_frame, bg="lightgray", width=400, height=300)
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)

        self.preview_label = tk.Label(
            self.preview_frame,
            text="사진이 여기에 표시됩니다",
            font=text_font,
            bg="lightgray"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # 2단계: 글귀 입력
        step2_frame = tk.LabelFrame(
            self.root,
            text="2단계: 글귀 입력 (선택사항)",
            font=text_font,
            padx=20,
            pady=10
        )
        step2_frame.pack(fill="x", padx=20, pady=10)

        self.text_input = scrolledtext.ScrolledText(
            step2_frame,
            font=text_font,
            height=4,
            wrap=tk.WORD
        )
        self.text_input.pack(fill="x", pady=10)
        self.text_input.insert("1.0", "원하는 글귀를 입력하세요...")
        self.text_input.bind("<FocusIn>", self.clear_placeholder)

        # 3단계: PDF 생성 및 출력
        step3_frame = tk.LabelFrame(
            self.root,
            text="3단계: PDF 만들고 인쇄하기",
            font=text_font,
            padx=20,
            pady=10
        )
        step3_frame.pack(fill="x", padx=20, pady=10)

        button_frame = tk.Frame(step3_frame)
        button_frame.pack(pady=10)

        self.pdf_button = tk.Button(
            button_frame,
            text="💾 PDF로 저장",
            font=button_font,
            command=self.create_pdf,
            bg="#2196F3",
            fg="white",
            padx=30,
            pady=15,
            cursor="hand2",
            state="disabled"
        )
        self.pdf_button.pack(side="left", padx=10)

        self.print_button = tk.Button(
            button_frame,
            text="🖨️ 바로 인쇄하기",
            font=button_font,
            command=self.print_pdf,
            bg="#FF9800",
            fg="white",
            padx=30,
            pady=15,
            cursor="hand2",
            state="disabled"
        )
        self.print_button.pack(side="left", padx=10)

    def clear_placeholder(self, event):
        """텍스트 입력 시 placeholder 제거"""
        if self.text_input.get("1.0", "end-1c") == "원하는 글귀를 입력하세요...":
            self.text_input.delete("1.0", "end")

    def select_image(self):
        """이미지 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="사진을 선택하세요",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("모든 파일", "*.*")
            ]
        )

        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            # PDF 및 출력 버튼 활성화
            self.pdf_button.config(state="normal")
            self.print_button.config(state="normal")

    def display_image(self, image_path):
        """선택한 이미지 미리보기"""
        try:
            # 이미지 로드
            image = Image.open(image_path)

            # 미리보기 크기에 맞게 조정
            display_width = 380
            display_height = 280

            # 비율 유지하며 크기 조정
            image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)

            # Tkinter용 이미지로 변환
            photo = ImageTk.PhotoImage(image)

            # 이미지 표시
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # 참조 유지

        except Exception as e:
            messagebox.showerror("오류", f"이미지를 불러올 수 없습니다:\n{str(e)}")

    def create_pdf(self):
        """PDF 파일 생성"""
        if not self.image_path:
            messagebox.showwarning("경고", "먼저 사진을 선택하세요!")
            return

        # 저장 위치 선택
        save_path = filedialog.asksaveasfilename(
            title="PDF 저장 위치를 선택하세요",
            defaultextension=".pdf",
            filetypes=[("PDF 파일", "*.pdf")],
            initialfile=f"사진_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        if not save_path:
            return

        try:
            self.generate_pdf(save_path)
            messagebox.showinfo("완료", f"PDF가 저장되었습니다!\n\n{save_path}")
        except Exception as e:
            messagebox.showerror("오류", f"PDF 생성 중 오류가 발생했습니다:\n{str(e)}")

    def print_pdf(self):
        """PDF 생성 후 바로 인쇄"""
        if not self.image_path:
            messagebox.showwarning("경고", "먼저 사진을 선택하세요!")
            return

        # 임시 PDF 파일 생성
        temp_pdf = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            f"temp_print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        try:
            self.generate_pdf(temp_pdf)

            if platform.system() == 'Windows':
                self.print_windows(temp_pdf)
            else:
                messagebox.showinfo("알림", "Windows에서만 직접 인쇄가 가능합니다.\nPDF를 저장한 후 수동으로 인쇄해주세요.")

        except Exception as e:
            messagebox.showerror("오류", f"인쇄 중 오류가 발생했습니다:\n{str(e)}")

    def generate_pdf(self, output_path):
        """PDF 생성 핵심 로직"""
        # PDF 캔버스 생성 (A4 크기)
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # 이미지 추가
        img = Image.open(self.image_path)
        img_width, img_height = img.size

        # A4 용지에 맞게 이미지 크기 조정 (여백 고려)
        max_width = width - 100  # 좌우 여백 50씩
        max_height = height - 200  # 상하 여백 및 텍스트 공간

        # 비율 유지하며 크기 계산
        ratio = min(max_width / img_width, max_height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio

        # 이미지 중앙 배치
        x = (width - new_width) / 2
        y = height - 50 - new_height  # 상단에서 50 포인트 아래

        c.drawImage(
            ImageReader(self.image_path),
            x, y,
            width=new_width,
            height=new_height,
            preserveAspectRatio=True
        )

        # 텍스트 추가 (입력된 경우)
        text_content = self.text_input.get("1.0", "end-1c").strip()
        if text_content and text_content != "원하는 글귀를 입력하세요...":
            c.setFont(self.pdf_font, 16)

            # 텍스트를 이미지 아래에 배치
            text_y = y - 40

            # 긴 텍스트 처리 (줄바꿈)
            lines = text_content.split('\n')
            for line in lines:
                # 한 줄이 너무 길면 자동 줄바꿈
                if c.stringWidth(line, self.pdf_font, 16) > max_width:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + " "
                        if c.stringWidth(test_line, self.pdf_font, 16) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                c.drawCentredString(width / 2, text_y, current_line.strip())
                                text_y -= 20
                            current_line = word + " "
                    if current_line:
                        c.drawCentredString(width / 2, text_y, current_line.strip())
                        text_y -= 20
                else:
                    c.drawCentredString(width / 2, text_y, line)
                    text_y -= 20

        c.save()

    def print_windows(self, pdf_path):
        """Windows에서 PDF 인쇄"""
        try:
            # 기본 프린터로 인쇄
            win32api.ShellExecute(
                0,
                "print",
                pdf_path,
                None,
                ".",
                0
            )
            messagebox.showinfo("완료", "인쇄 작업이 시작되었습니다!")
        except Exception as e:
            messagebox.showerror("오류", f"인쇄 중 오류가 발생했습니다:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageToPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
