FROM gorialis/discord.py

WORKDIR /app

ADD . /app
RUN python -m pip install -r requirements.txt
RUN python -m pip install -e .

CMD ["python", "-m", "cwcbot"]
