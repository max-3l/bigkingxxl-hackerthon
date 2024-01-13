<template>
  <q-form @submit="onSubmit" v-show="showInput" class="input">
    <q-input rounded outlined v-model="prompt" label="Prompt" />
  </q-form>
  <div v-show="!showInput" class="card">
    <q-card class="bottom-space">
      <q-card-section>
        <q-card-title>
          <strong>🙋 Your Prompt</strong> <br>
        </q-card-title>
        <q-card-main>
          {{ prompt }}
        </q-card-main>
      </q-card-section>
    </q-card>
    <!-- DIV to align two cards horizontally -->
    <div class="horizontal-cards">
      <div class="vertical-cards">
        <q-card class="full-card" flat>
          <q-card-section>
            <q-card-title>
              <strong>🥴 Insights</strong> <br>
            </q-card-title>
            <q-card-main>
              Confidence Chat GPT 3.5 - {{ (confidence * 100).toFixed(2) }}%
              <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
              <svg class="full-card svg">
                <rect x="1" y="1" rx="1%" width="99%" height="15"
                  style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                <rect x="2" y="2" rx="1%" :width="confidence * 99 + '%'" height="13"
                  :style="'fill:' + confidenceColor + ';stroke-width:0;stroke:rgb(0,0,0)'" />
              </svg>
              <strong>Annotations</strong> <br>
              <q-chip clickable :outline="showAnnotationExplanation == 0" label="🤖 Good Robot" color="green"
                @click="showAnnotationExplanation = showAnnotationExplanation == 0 ? -1 : 0" />
              <q-chip clickable :outline="showAnnotationExplanation == 1" label="🤖 Bad Robot" color="red"
                @click="showAnnotationExplanation = showAnnotationExplanation == 1 ? -1 : 1" />
              <div class="top-space some-padding" :v-show="showAnnotationExplanation != -1">
                {{ annotationExplanation }}
              </div>
            </q-card-main>
          </q-card-section>
        </q-card>
      </div>

      <q-card class="full-card">
        <q-card-section>
          <q-card-title>
            <strong>🤖 AI Response</strong> <br>
          </q-card-title>
          <q-card-main>
            {{ response }}
          </q-card-main>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
} from 'vue';
import * as chroma from 'chroma-js';

export default defineComponent({
  name: 'ExampleComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    active: {
      type: Boolean
    }
  },
  setup() {
    return {
      prompt: ref(''),
      response: ref(''),
      confidence: ref(0.0),
      showInput: ref(true),
      confidenceColor: ref('#000000'),
      showAnnotationExplanation: ref(-1)
    };
  },
  computed: {
    annotationExplanation(): string {
      if (this.showAnnotationExplanation == 0) {
        return 'This is a good robot response because it is very similar to the prompt.';
      }
      if (this.showAnnotationExplanation == 1) {
        return 'This is a bad robot response because it is very different from the prompt.';
      }
      return ''
    }
  },
  methods: {
    onSubmit() {
      console.log(this.prompt);
      this.showInput = false;
      this.sendRequest();
    },
    async animateConfidence(confidence: number) {
      const f = chroma.scale(['red', '#c9b23c', 'green']);
      this.confidence = 0;
      const interval = setInterval(() => {
        this.confidence = this.confidence + 0.01;
        this.confidenceColor = f(this.confidence).hex();
        if (this.confidence >= confidence) {
          clearInterval(interval);
        }
      }, 5);
    },
    async sendRequest() {
      const stream = await fetch('http://localhost:8000/stream');
      if (!stream.body) {
        console.log('no body');
        return;
      }
      this.animateConfidence(0.9);
      const reader = stream.body.pipeThrough(new TextDecoderStream()).getReader();
      let done = false;
      while (!done) {
        const { value, done: done2 } = await reader.read();
        if (done2) {
          done = true;
          break;
        }
        this.response = this.response + value.toString();
      }
    }
  }
});
</script>

<style>
.input {
  width: 90%
}

.card {
  width: 90%
}

.full-card {
  width: 100%;
}

.bottom-space {
  margin-bottom: 10px;
}

.top-space {
  margin-top: 10px;
}

.some-padding {
  padding: 10px;
}

.horizontal-cards {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 10px;
}

.svg {
  height: 20px;
}
</style>
