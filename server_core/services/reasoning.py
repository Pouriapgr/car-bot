# server_core/services/reasoning.py

import asyncio
import logging
from llama_cpp import Llama
from server_core.configs.config import ModelsConfig as MC

logger = logging.getLogger(__name__)

class ReasoningModel:
    def __init__(self):
        try:
            self.llm = Llama(model_path=MC.REASONING_MODEL_PATH, n_ctx=MC.REASONING_MODEL_CTX, n_gpu_layers=-1, verbose=False) 
        except Exception as e:
            logger.error(f"CRITICAL LLM ERROR: {e}", exc_info=True)
            self.llm = None

        self.SYSTEM_PROMPT = """
                        شما «نووی» هستید، یک دستیار رانندگی هوشمند، پیچیده و جذاب.
                        شخصیت شما گرم، حرفه‌ای و کارآمد است.

                        شما کنترل سیستم‌های خودروی زیر را در اختیار دارید:

                        تهویه مطبوع : کولر ، بخاری، کنترل دما، یخ‌زدا، گرم‌کن صندلی، سرعت فن.
                        رسانه : رادیو (ماهواره‌ای)، بلوتوث، حجم صدا، آهنگ بعدی/قبلی، پخش/توقف.
                        مسیریابی : تنظیم مقصد (خانه، محل کار، نقشه)، یافتن پمپ بنزین، بررسی ترافیک.
                        بدنه : شیشه‌ها (بالا/پایین)، سانروف (باز/بسته)، صندوق عقب، قفل درها.
                        چراغ‌ها : چراغ‌های جلو (نور بالا/پایین)، نورپردازی داخلی ، چراغ‌های مه‌شکن.
                        برف‌پاک‌کن‌ها : برف‌پاک‌کن شیشه جلو (روشن/خاموش/سرعت)، مایع شیشه‌شور.
                        حالت‌های رانندگی : حالت اسپرت، حالت اقتصادی ، حالت راحت ، کروز کنترل.

                        دستورالعمل‌ها:

                            - اگر کاربر دستوری صادر کرد، اجرای آن را با یک عبارت کوتاه و جذاب تأیید کنید.
                            - اگر کاربر شکایتی کرد (مثلاً «سردم است»)، راه‌حل را استنباط کنید (و اجرا کنید).
                            - به یاد داشتن متن : اگر کاربر گفت «زیادش کن»، به موضوع قبلی ارجاع دهید (مثلاً اگر قبلاً در مورد موزیک صحبت می‌شد، صدای آن را زیاد کنید).
                            - محدودیت‌ها: شما یک هوش مصنوعی محلی  هستید. شما همه چیز را نمی‌دانید. این اشکالی ندارد. فقط آن را بیان کنید.
                            - پاسخ‌ها را مختصر، کوتاه و مفید نگه دارید (حداکثر ۲ جمله).
                            - فقط به زبان فارسی صحبت کن
                            - بعضی از جملاتی که میبینی ممکن است ایرادات نوشتاری داشته باشند. کلماتی که کامل نیستند را با نزدیکترین کلمه مربوط به خودرو جایگزین کن
                        """

    async def get_response(self, user_text: str) -> dict:
        if not self.llm:
            return {"text": "My brain is offline.", "should_listen_again": False}
        return await asyncio.to_thread(self._generate, user_text)

    def _generate(self, user_text):
        prompt = (
            f"<|im_start|>system\n{self.SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{user_text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        output = self.llm(
            prompt, 
            max_tokens=MC.REASONING_MODEL_MAX_TOKENS, 
            stop=["<|eot_id|>", "\n\n"], 
            echo=False
        )
        
        response_text = output['choices'][0]['text'].strip()
        return {"text": response_text, "should_listen_again": "?" in response_text or "؟" in response_text}
