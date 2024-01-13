<template>
  <div v-if="showInput" class="input horizontal-cards">
    <q-form @submit="onSubmit" class="full-card">
      <q-input rounded outlined v-model="prompt" label="Prompt" class="full-card" />
    </q-form>
    <q-select rounded outlined v-model="model" :options="models" label="Model" class="third-card" />
  </div>
  <div v-show="!showInput" class="card">
    <q-card class="bottom-space">
      <q-card-section>
        <q-card-title>
          <div class="no-spacing prompt-header">
            <strong class="header-label">🙋 Your Prompt</strong>
            <div class="no-spacing" @click="selectModel">
              <strong> {{ model }} </strong>
            </div>
          </div>
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
              <strong class="header-label">🥴 Insights</strong> <br>
            </q-card-title>
            <q-card-main>
              <strong>Expertise</strong> <br>
              <div class="no-spacing">
                Chat GPT 3.5 - {{ (confidence * 100).toFixed(2) }}%
                <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
                <svg class="full-card svg">
                  <rect x="1" y="1" rx="1%" width="99%" height="15"
                    style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                  <rect x="2" y="2" rx="1%" :width="confidence * 99 + '%'" height="13"
                    :style="'fill:' + confidenceColor + ';stroke-width:0;stroke:rgb(0,0,0)'" />
                </svg>
              </div>
              <div class="no-spacing">
                Chat GPT 3.5 - {{ (confidence * 100).toFixed(2) }}%
                <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
                <svg class="full-card svg">
                  <rect x="1" y="1" rx="1%" width="99%" height="15"
                    style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                  <rect x="2" y="2" rx="1%" :width="confidence * 99 + '%'" height="13"
                    :style="'fill:' + confidenceColor + ';stroke-width:0;stroke:rgb(0,0,0)'" />
                </svg>
              </div>
              <strong>Annotations</strong> <br>
              <q-chip clickable :outline="showAnnotationExplanation == 0" label="🤖 Good Robot" color="green"
                @click="showAnnotationExplanation = showAnnotationExplanation == 0 ? -1 : 0" />
              <q-chip clickable :outline="showAnnotationExplanation == 1" label="🤖 Bad Robot" color="red"
                @click="showAnnotationExplanation = showAnnotationExplanation == 1 ? -1 : 1" />
              <div class="top-space" v-if="showAnnotationExplanation != -1">
                <strong>Annotation Details</strong> <br>
                {{ annotationExplanation }}
                <div class="thumbs">
                  <q-btn flat @click="thumbsUp">👍</q-btn>
                  <q-btn flat @click="thumbsDown">👎</q-btn>
                </div>
              </div>
            </q-card-main>
          </q-card-section>
        </q-card>
      </div>

      <q-card flat class="full-card">
        <q-card-section>
          <q-card-title>
            <div class="no-spacing horizontal-cards">
              <strong class="header-label">🤖 AI Response</strong>
              <div class="no-spacing">
                Confidence - {{ (confidence * 100).toFixed(2) }}%
                <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
                <svg class="full-card svg">
                  <rect x="1" y="1" rx="1%" width="99%" height="15"
                    style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                  <rect x="2" y="2" rx="1%" :width="confidence * 99 + '%'" height="13"
                    :style="'fill:' + confidenceColor + ';stroke-width:0;stroke:rgb(0,0,0)'" />
                </svg>
              </div>
            </div>
          </q-card-title>
          <q-card-main>
            {{ response }}
            <q-form v-show="done && !annotationSubmitted" @submit="submitAnnotation" class="horizontal-cards top-space">
              <q-input filled v-model="customAnnotation" label="Your annotation" dense class="full-width">
              </q-input>
              <q-btn dense flat icon="send" type="submit" />
            </q-form>
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
      showAnnotationExplanation: ref(-1),
      model: ref('chat-gpt3'),
      models: ref(['chat-gpt3', 'chat-gpt3.5', 'chat-gpt4']),
      done: ref(false),
      annotationSubmitted: ref(false),
      customAnnotation: ref(''),
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
  watch: {
    model() {
      this.showAnnotationExplanation = -1
      this.response = ''
      this.confidence = 0.0
      this.showInput = true
      this.confidenceColor = '#000000'
      this.done = false
      this.annotationSubmitted = false
      this.customAnnotation = ''
    }
  },
  methods: {
    submitAnnotation(e: Event) {
      console.log('submit annotation')
      e.preventDefault();
      if (this.customAnnotation == '') {
        console.log('no annotation')
        return
      }
      console.log('submit annotation')
      this.annotationSubmitted = true
    },
    selectModel() {
      this.$q.dialog({
        title: 'Select Model',
        message: 'Select a model to use for the response.',
        options: {
          type: 'radio',
          model: this.model,
          items:
            [{
              label: 'Chat GPT 3',
              value: 'chat-gpt3'
            },
            {
              label: 'Chat GPT 3.5',
              value: 'chat-gpt3.5'
            },
            {
              label: 'Chat GPT 4',
              value: 'chat-gpt4'
            }]
        },
        cancel: true,
        persistent: true
      }).onOk((model: string) => {
        this.model = model;
      });
      console.log('select model');
    },
    onSubmit(e: Event) {
      e.preventDefault();
      console.log(this.prompt);
      this.showInput = false;
      this.sendRequest();
    },
    thumbsUp() {
      console.log('thumbs up');
    },
    thumbsDown() {
      console.log('thumbs down')
    },
    async animateConfidence(confidence: number) {
      const f = chroma.scale(['red', '#c9b23c', 'green'])
      this.confidence = 0
      const interval = setInterval(() => {
        this.confidence = this.confidence + 0.01
        this.confidenceColor = f(this.confidence).hex()
        if (this.confidence >= confidence) {
          clearInterval(interval)
        }
      }, 5);
    },
    async sendRequest() {
      const stream = await fetch('http://localhost:8000/stream')
      if (!stream.body) {
        console.log('no body')
        return;
      }
      this.animateConfidence(0.9)
      const reader = stream.body.pipeThrough(new TextDecoderStream()).getReader()
      let done = false
      while (!done) {
        const { value, done: done2 } = await reader.read()
        if (done2) {
          done = true
          this.done = true
          break
        }
        this.response = this.response + value.toString()
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

.auto-width {
  width: auto;
}

.full-card {
  width: 100%;
}

.third-card {
  width: 33%;
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

.no-spacing {
  margin: 0px;
  padding: 0px;
}

.prompt-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.header-label {
  font-size: 20px;
}
</style>
