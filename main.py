"""
이미지-텍스트-PDF 변환 및 프린터 출력 프로그램
어르신용 간단한 UI
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
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
        
        # 창 아이콘 설정 (icon.ico 파일이 있는 경우)
        try:
            if os.path.exists('icon.ico'):
                self.root.iconbitmap('icon.ico')
        except:
            pass  # 아이콘 파일이 없거나 오류 시 무시
        
        # 창 크기 설정 (세로 100px 축소)
        window_width = 1100
        window_height = 900
        
        # 화면 중앙에 위치시키기
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # 변수 초기화
        self.image_path = None
        self.image_display = None
        self.image_ratio = 50  # 사진 비율 (기본 50%)

        # 한글 폰트 설정 (Windows 기본 폰트)
        self.setup_fonts()

        # UI 구성
        self.create_widgets()
        
        # 드래그 앤 드롭 설정
        self.setup_drag_drop()
        
        # step1_frame 저장 (드래그 앤 드롭용)
        self.step1_frame = None

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
        
        # step1_frame 저장 (드래그 앤 드롭용)
        self.step1_frame = step1_frame

        # 좌우 레이아웃을 위한 프레임
        content_frame = tk.Frame(step1_frame)
        content_frame.pack(fill="both", expand=True, pady=5)

        # 왼쪽: 이미지 미리보기
        self.preview_frame = tk.Frame(content_frame, bg="lightgray", relief="solid", borderwidth=2, height=150)
        self.preview_frame.pack(side="left", fill="both", expand=True)
        self.preview_frame.pack_propagate(False)  # 크기 고정

        self.preview_label = tk.Label(
            self.preview_frame,
            text="사진을 선택하거나\n여기로 드래그하세요",
            font=('맑은 고딕', 13),
            bg="lightgray",
            fg="gray"
        )
        self.preview_label.pack(fill="both", expand=True, padx=20, pady=20)

        # 오른쪽: 버튼 영역
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side="left", padx=(20, 0), fill="y")

        self.select_button = tk.Button(
            right_frame,
            text="📁 사진\n선택하기",
            font=button_font,
            command=self.select_image,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=30,
            cursor="hand2"
        )
        self.select_button.pack(anchor="center")

        # 2단계: 글귀 입력
        step2_frame = tk.LabelFrame(
            self.root,
            text="2단계: 글귀 입력 (선택사항)",
            font=text_font,
            padx=20,
            pady=10
        )
        step2_frame.pack(fill="x", padx=20, pady=10)

        # 좌우 레이아웃
        input_container = tk.Frame(step2_frame)
        input_container.pack(fill="both", expand=False)

        # 왼쪽: 글귀 입력
        left_input_frame = tk.Frame(input_container)
        left_input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.text_input = scrolledtext.ScrolledText(
            left_input_frame,
            font=text_font,
            height=10,
            wrap=tk.WORD
        )
        self.text_input.pack(fill="both", expand=False)
        self.text_input.insert("1.0", "원하는 글귀를 입력하세요...")
        self.text_input.bind("<FocusIn>", self.clear_placeholder)
        self.text_input.bind("<KeyRelease>", self.update_preview)

        # 오른쪽: 인쇄 미리보기
        right_preview_frame = tk.Frame(input_container)
        right_preview_frame.pack(side="left", fill="y", expand=False, padx=(10, 0))

        preview_title = tk.Label(
            right_preview_frame,
            text="📄 인쇄 미리보기",
            font=('맑은 고딕', 13, 'bold')
        )
        preview_title.pack(pady=(0, 5))

        # A4 비율: 210mm x 297mm = 1:1.414
        preview_display_width = 180
        preview_display_height = int(preview_display_width * 1.414)

        self.print_preview_frame = tk.Frame(
            right_preview_frame,
            bg="white",
            relief="solid",
            borderwidth=1,
            width=preview_display_width,
            height=preview_display_height
        )
        self.print_preview_frame.pack(fill="none", expand=False)
        self.print_preview_frame.pack_propagate(False)

        self.print_preview_label = tk.Label(
            self.print_preview_frame,
            text="사진을 선택하면\n미리보기가 표시됩니다",
            font=('맑은 고딕', 10),
            bg="white",
            fg="gray"
        )
        self.print_preview_label.pack(fill="both", expand=True)
        
        # 사진/글귀 비율 조절 슬라이더
        ratio_frame = tk.Frame(step2_frame)
        ratio_frame.pack(fill="x", pady=10)
        
        ratio_label = tk.Label(
            ratio_frame,
            text="사진 크기 비율:",
            font=('맑은 고딕', 12)
        )
        ratio_label.pack(side="left", padx=10)
        
        self.ratio_slider = tk.Scale(
            ratio_frame,
            from_=20,
            to=80,
            orient=tk.HORIZONTAL,
            length=300,
            font=('맑은 고딕', 10),
            label="",
            command=self.update_ratio_label
        )
        self.ratio_slider.set(50)
        self.ratio_slider.pack(side="left", padx=10)
        
        self.ratio_value_label = tk.Label(
            ratio_frame,
            text="50% (글귀 50%)",
            font=('맑은 고딕', 12),
            width=20
        )
        self.ratio_value_label.pack(side="left", padx=10)

        # 3단계: PDF 생성 및 출력
        step3_frame = tk.LabelFrame(
            self.root,
            text="3단계: PDF 만들고 인쇄하기",
            font=text_font,
            padx=20,
            pady=10
        )
        step3_frame.pack(fill="x", padx=20, pady=10)

        # 좌우 레이아웃
        button_container = tk.Frame(step3_frame)
        button_container.pack(fill="x")

        # 왼쪽: 안내 메시지
        left_info_frame = tk.Frame(button_container)
        left_info_frame.pack(side="left", fill="both", expand=True)

        info_label = tk.Label(
            left_info_frame,
            text="PDF로 저장하거나 바로 프린터로 인쇄할 수 있습니다.",
            font=('맑은 고딕', 13),
            fg="gray"
        )
        info_label.pack(anchor="w", pady=10)

        # 오른쪽: 버튼 영역
        button_frame = tk.Frame(button_container)
        button_frame.pack(side="right", padx=(10, 0))

        self.pdf_button = tk.Button(
            button_frame,
            text="💾 PDF로 저장",
            font=button_font,
            command=self.create_pdf,
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            state="disabled"
        )
        self.pdf_button.pack(side="left", padx=(0, 5))

        self.print_button = tk.Button(
            button_frame,
            text="🖨️ 바로 인쇄하기",
            font=button_font,
            command=self.print_pdf,
            bg="#FF9800",
            fg="white",
            padx=10,
            pady=5,
            cursor="hand2",
            state="disabled"
        )
        self.print_button.pack(side="left")

    def setup_drag_drop(self):
        """드래그 앤 드롭 설정"""
        # 1단계 전체 프레임에 드래그 앤 드롭 적용
        if hasattr(self, 'step1_frame') and self.step1_frame:
            self.step1_frame.drop_target_register(DND_FILES)
            self.step1_frame.dnd_bind('<<Drop>>', self.drop_image)
        
        # 미리보기 영역에도 적용
        self.preview_frame.drop_target_register(DND_FILES)
        self.preview_frame.dnd_bind('<<Drop>>', self.drop_image)
        self.preview_label.drop_target_register(DND_FILES)
        self.preview_label.dnd_bind('<<Drop>>', self.drop_image)

    def drop_image(self, event):
        """드래그 앤 드롭으로 이미지 추가"""
        try:
            # 파일 경로 추출
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0].strip('{}')
                # 이미지 파일인지 확인
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    self.image_path = file_path
                    self.display_image(file_path)
                    # PDF 및 출력 버튼 활성화
                    self.pdf_button.config(state="normal")
                    self.print_button.config(state="normal")
                    # 미리보기 업데이트
                    self.root.after(100, self.update_preview)
                else:
                    messagebox.showwarning("경고", "이미지 파일만 사용할 수 있습니다.\n(JPG, PNG, BMP, GIF)")
        except Exception as e:
            messagebox.showerror("오류", f"파일을 불러올 수 없습니다:\n{str(e)}")

    def update_ratio_label(self, value):
        """비율 슬라이더 값 업데이트"""
        self.image_ratio = int(value)
        text_ratio = 100 - self.image_ratio
        self.ratio_value_label.config(text=f"{self.image_ratio}% (글귀 {text_ratio}%)")
        # 미리보기 업데이트
        self.update_preview()

    def update_preview(self, event=None):
        """인쇄 미리보기 업데이트"""
        if not self.image_path:
            return
        
        try:
            # A4 비율 고정 (210mm x 297mm = 1:1.414)
            display_width = 180
            display_height = int(display_width * 1.414)  # 약 255
            
            # 새 이미지 생성 (A4 용지 배경)
            from PIL import Image, ImageDraw, ImageFont
            preview_img = Image.new('RGB', (display_width, display_height), 'white')
            draw = ImageDraw.Draw(preview_img)
            
            # 원본 이미지 로드 및 비율에 따라 배치
            img = Image.open(self.image_path)
            
            # 텍스트 확인
            text_content = self.text_input.get("1.0", "end-1c").strip()
            has_text = text_content and text_content != "원하는 글귀를 입력하세요..."
            
            # 공간 배분 - 글귀가 없어도 비율 적용
            image_space_ratio = self.image_ratio / 100.0
            
            # 항상 비율에 따라 이미지 높이 계산
            img_height = int((display_height - 10) * image_space_ratio)
            
            # 이미지 크기 조정
            img_copy = img.copy()
            img_copy.thumbnail((display_width - 10, img_height), Image.Resampling.LANCZOS)
            
            # 이미지를 중앙에 배치
            img_x = (display_width - img_copy.width) // 2
            img_y = 5
            preview_img.paste(img_copy, (img_x, img_y))
            
            # 텍스트 추가
            if has_text:
                text_y = img_y + img_copy.height + 5
                text_height = display_height - text_y - 5
                
                # 텍스트를 줄바꿈하여 표시
                lines = text_content.split('\n')
                
                # 글자 수에 따라 기본 폰트 크기 계산
                total_chars = len(text_content)
                base_font_size = max(5, int(display_height / 40))  # 기본 크기
                
                # 글자 수가 많을수록 폰트 축소
                if total_chars > 500:
                    font_size = max(4, int(base_font_size * 0.5))
                elif total_chars > 300:
                    font_size = max(4, int(base_font_size * 0.6))
                elif total_chars > 200:
                    font_size = max(5, int(base_font_size * 0.7))
                elif total_chars > 100:
                    font_size = max(5, int(base_font_size * 0.85))
                else:
                    font_size = base_font_size
                
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # 예상 줄 수 계산
                line_height = font_size + 2
                max_lines = int(text_height / line_height)
                
                # 실제 줄바꿈 처리
                wrapped_lines = []
                chars_per_line = max(10, int(display_width / (font_size * 0.6)))  # 한 줄에 들어갈 글자 수 추정
                
                for line in lines:
                    if not line.strip():
                        wrapped_lines.append("")
                        continue
                    
                    # 긴 줄을 자동 줄바꿈
                    while len(line) > chars_per_line:
                        wrapped_lines.append(line[:chars_per_line])
                        line = line[chars_per_line:]
                    if line:
                        wrapped_lines.append(line)
                
                # 줄 수가 여전히 많으면 추가로 폰트 축소
                if len(wrapped_lines) > max_lines:
                    adjustment_ratio = max_lines / len(wrapped_lines)
                    font_size = max(4, int(font_size * adjustment_ratio * 0.95))
                    line_height = font_size + 2
                    
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                    
                    # 줄바꿈 다시 계산
                    wrapped_lines = []
                    chars_per_line = max(10, int(display_width / (font_size * 0.6)))
                    
                    for line in lines:
                        if not line.strip():
                            wrapped_lines.append("")
                            continue
                        
                        while len(line) > chars_per_line:
                            wrapped_lines.append(line[:chars_per_line])
                            line = line[chars_per_line:]
                        if line:
                            wrapped_lines.append(line)
                
                # 텍스트 그리기
                y_offset = text_y
                for line in wrapped_lines:
                    if y_offset + line_height < display_height - 3:
                        draw.text((5, y_offset), line, fill='black', font=font)
                        y_offset += line_height
                    else:
                        break  # 공간이 부족하면 중단
            
            # Tkinter 이미지로 변환
            photo = ImageTk.PhotoImage(preview_img)
            self.print_preview_label.config(image=photo, text="")
            self.print_preview_label.image = photo
            
        except Exception as e:
            print(f"미리보기 업데이트 오류: {e}")  # 디버깅용
            import traceback
            traceback.print_exc()  # 상세 오류 출력

    def clear_placeholder(self, event):
        """텍스트 입력 시 placeholder 제거"""
        if self.text_input.get("1.0", "end-1c") == "원하는 글귀를 입력하세요...":
            self.text_input.delete("1.0", "end")
        self.update_preview()

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
            # 미리보기 업데이트 (약간의 지연 후 실행)
            self.root.after(100, self.update_preview)

    def display_image(self, image_path):
        """선택한 이미지 미리보기"""
        try:
            # 이미지 로드
            image = Image.open(image_path)

            # 미리보기 프레임의 현재 크기 가져오기
            self.preview_frame.update_idletasks()
            frame_width = self.preview_frame.winfo_width()
            frame_height = self.preview_frame.winfo_height()
            
            # 최소 크기 보장
            if frame_width < 100:
                frame_width = 600
            if frame_height < 100:
                frame_height = 150

            # 여백을 고려한 디스플레이 크기
            display_width = frame_width - 40
            display_height = frame_height - 40

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
            
            # 저장 완료 후 파일 열기 확인
            response = messagebox.askyesno(
                "저장 완료", 
                f"PDF가 저장되었습니다!\n\n{save_path}\n\n파일을 열어보시겠습니까?"
            )
            
            if response:
                # PDF 파일 열기
                if platform.system() == 'Windows':
                    os.startfile(save_path)
                else:
                    import subprocess
                    subprocess.call(('xdg-open', save_path))
                    
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

        # 텍스트 내용 확인
        text_content = self.text_input.get("1.0", "end-1c").strip()
        has_text = text_content and text_content != "원하는 글귀를 입력하세요..."

        # 사진 비율에 따라 공간 배분
        image_space_ratio = self.image_ratio / 100.0
        text_space_ratio = (100 - self.image_ratio) / 100.0

        # A4 용지에 맞게 이미지 크기 조정 (여백 절반으로 축소)
        max_width = width - 50  # 좌우 여백 25씩 (기존 50에서 절반)
        
        if has_text:
            # 텍스트가 있으면 비율에 따라 공간 분배
            max_height = (height - 75) * image_space_ratio  # 상하 여백 75 (기존 150에서 절반)
        else:
            # 텍스트가 없으면 전체 공간 사용
            max_height = height - 75

        # 비율 유지하며 크기 계산
        ratio = min(max_width / img_width, max_height / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio

        # 이미지 중앙 배치
        x = (width - new_width) / 2
        y = height - 25 - new_height  # 상단에서 25 포인트 아래 (기존 50에서 절반)

        c.drawImage(
            ImageReader(self.image_path),
            x, y,
            width=new_width,
            height=new_height,
            preserveAspectRatio=True
        )

        # 텍스트 추가 (입력된 경우)
        if has_text:
            # 텍스트 영역 시작 위치
            text_y_start = y - 20  # 이미지와 텍스트 간격 축소 (기존 30에서 20)
            text_area_height = (height - 75) * text_space_ratio
            
            # 텍스트 줄 분리 및 길이 계산
            lines = text_content.split('\n')
            all_lines = []
            
            # 기본 폰트 크기 (1.5배 증가)
            base_font_size = 24
            
            # 좌측 여백 설정
            left_margin = 25
            
            # 각 줄을 적절히 분할
            for line in lines:
                if not line.strip():
                    all_lines.append("")
                    continue
                    
                # 한 줄이 너무 길면 자동 줄바꿈
                if c.stringWidth(line, self.pdf_font, base_font_size) > max_width:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + " "
                        if c.stringWidth(test_line, self.pdf_font, base_font_size) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                all_lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        all_lines.append(current_line.strip())
                else:
                    all_lines.append(line)
            
            # 필요한 총 높이 계산 및 폰트 크기 자동 조절
            line_spacing = base_font_size + 6
            total_text_height = len(all_lines) * line_spacing
            
            # 텍스트가 영역을 초과하면 폰트 크기 축소
            if total_text_height > text_area_height:
                # 비율에 맞춰 폰트 축소
                font_size = int(base_font_size * (text_area_height / total_text_height) * 0.95)  # 0.95 여유 공간
                font_size = max(8, font_size)  # 최소 8pt
                line_spacing = font_size + 4
                
                # 폰트 크기를 줄인 후 다시 줄바꿈 계산
                all_lines = []
                for line in lines:
                    if not line.strip():
                        all_lines.append("")
                        continue
                        
                    if c.stringWidth(line, self.pdf_font, font_size) > max_width:
                        words = line.split()
                        current_line = ""
                        for word in words:
                            test_line = current_line + word + " "
                            if c.stringWidth(test_line, self.pdf_font, font_size) <= max_width:
                                current_line = test_line
                            else:
                                if current_line:
                                    all_lines.append(current_line.strip())
                                current_line = word + " "
                        if current_line:
                            all_lines.append(current_line.strip())
                    else:
                        all_lines.append(line)
                
                # 다시 한번 높이 체크 후 필요시 추가 축소
                total_text_height = len(all_lines) * line_spacing
                if total_text_height > text_area_height:
                    font_size = int(font_size * (text_area_height / total_text_height) * 0.95)
                    font_size = max(7, font_size)  # 최소 7pt로 더 축소
                    line_spacing = font_size + 3
            else:
                font_size = base_font_size
            
            c.setFont(self.pdf_font, font_size)
            
            # 텍스트 그리기 (왼쪽 정렬)
            text_y = text_y_start
            for line in all_lines:
                if text_y > 25:  # 페이지 하단 여백 확인 (기존 50에서 25)
                    c.drawString(left_margin, text_y, line)  # 왼쪽 정렬
                    text_y -= line_spacing
                else:
                    # 페이지를 벗어나는 경우 경고 (디버깅용, 실제로는 폰트가 충분히 작아져야 함)
                    break

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
    root = TkinterDnD.Tk()  # 드래그 앤 드롭 지원
    app = ImageToPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
